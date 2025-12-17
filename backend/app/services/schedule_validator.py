"""
Schedule Validation Service - Conflict Detection and Temporal Scheduling

This module provides functionality to detect and prevent temporal conflicts
in satellite communication schedules, ensuring collision avoidance and
optimal scheduling decisions.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text
from app.db.models import PassSchedule, Satellite

from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DEFAULT_PASSES_PER_SATELLITE = os.getenv("DEFAULT_PASSES_PER_SATELLITE", "5")

class ConflictType:
    """Types of schedule conflicts that can occur."""
    TEMPORAL_OVERLAP = "temporal_overlap"
    GROUND_STATION_CONFLICT = "ground_station_conflict"
    SATELLITE_ACCESS_CONFLICT = "satellite_access_conflict"
    MINIMUM_SEPARATION_VIOLATION = "minimum_separation_violation"


class ScheduleConflict:
    """Represents a detected schedule conflict."""
    
    def __init__(self, conflict_type: str, description: str, conflicting_pass_id: int = None, 
                 suggested_time: Optional[datetime] = None, severity: str = "high"):
        self.conflict_type = conflict_type
        self.description = description
        self.conflicting_pass_id = conflicting_pass_id
        self.suggested_time = suggested_time
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary for JSON serialization."""
        return {
            "conflict_type": self.conflict_type,
            "description": self.description,
            "conflicting_pass_id": self.conflicting_pass_id,
            "suggested_time": self.suggested_time.isoformat() + "Z" if self.suggested_time else None,
            "severity": self.severity
        }


def check_temporal_conflicts(
    new_pass_start: datetime,
    new_pass_end: datetime,
    new_ground_station: str,
    new_satellite_norad_id: int,
    db: Session,
    conflict_window_minutes: int = 10
) -> List[ScheduleConflict]:
    """
    Check for temporal conflicts with existing pass schedules.
    
    Args:
        new_pass_start: Start time of the new pass
        new_pass_end: End time of the new pass
        new_ground_station: Ground station for the new pass
        new_satellite_norad_id: NORAD ID of the satellite
        db: Database session
        conflict_window_minutes: Minimum time separation required (buffer)
        
    Returns:
        List of detected conflicts
    """
    conflicts = []
    
    try:
        # Define the conflict window (buffer before and after the new pass)
        buffer_timedelta = timedelta(minutes=conflict_window_minutes)
        window_start = new_pass_start - buffer_timedelta
        window_end = new_pass_end + buffer_timedelta
        
        # Query for overlapping passes using SQLAlchemy
        # Passes that overlap if: existing.start < new.end AND existing.end > new.start
        overlapping_passes = db.query(PassSchedule).filter(
            and_(
                PassSchedule.start_time < window_end,
                PassSchedule.end_time > window_start
            )
        ).all()
        
        for existing_pass in overlapping_passes:
            # Check for ground station conflicts (same ground station)
            if existing_pass.ground_station == new_ground_station:
                conflicts.append(ScheduleConflict(
                    conflict_type=ConflictType.GROUND_STATION_CONFLICT,
                    description=f"Ground station '{new_ground_station}' is already scheduled for pass {existing_pass.pass_id} "
                              f"from {existing_pass.start_time} to {existing_pass.end_time}",
                    conflicting_pass_id=existing_pass.pass_id,
                    severity="high"
                ))
            
            # Check for satellite access conflicts (same satellite, but this is usually OK for different ground stations)
            if existing_pass.satellite_norad_id == new_satellite_norad_id:
                # This is generally not a conflict unless it's the same ground station
                pass  # Handled by ground station conflict above
            
            # Check for minimum separation violations
            time_separation = abs((existing_pass.start_time - new_pass_start).total_seconds()) / 60
            if time_separation < conflict_window_minutes:
                conflicts.append(ScheduleConflict(
                    conflict_type=ConflictType.MINIMUM_SEPARATION_VIOLATION,
                    description=f"Pass {existing_pass.pass_id} is only {time_separation:.1f} minutes apart "
                              f"from the new pass, violating minimum separation of {conflict_window_minutes} minutes",
                    conflicting_pass_id=existing_pass.pass_id,
                    severity="medium"
                ))
        
        logger.info(f"Checked temporal conflicts: {len(conflicts)} conflicts found")
        return conflicts
        
    except Exception as e:
        logger.error(f"Error checking temporal conflicts: {e}")
        return [ScheduleConflict(
            conflict_type=ConflictType.TEMPORAL_OVERLAP,
            description=f"Error checking conflicts: {str(e)}",
            severity="high"
        )]


def find_next_available_slot(
    requested_start: datetime,
    requested_duration_minutes: int,
    ground_station: str,
    satellite_norad_id: int,
    db: Session,
    search_hours_ahead: int = 168,  # 1 week
    max_search_iterations: int = 50
) -> Optional[datetime]:
    """
    Find the next available time slot that doesn't conflict with existing schedules.
    
    Args:
        requested_start: Desired start time
        requested_duration_minutes: Duration of the pass in minutes
        ground_station: Ground station name
        satellite_norad_id: NORAD ID of the satellite
        db: Database session
        search_hours_ahead: How many hours ahead to search
        max_search_iterations: Maximum number of time slots to check
        
    Returns:
        Next available start time, or None if no slot found
    """
    try:
        current_time = requested_start
        search_end = current_time + timedelta(hours=search_hours_ahead)
        iteration = 0
        
        while current_time < search_end and iteration < max_search_iterations:
            proposed_end = current_time + timedelta(minutes=requested_duration_minutes)
            
            # Check for conflicts
            conflicts = check_temporal_conflicts(
                new_pass_start=current_time,
                new_pass_end=proposed_end,
                new_ground_station=ground_station,
                new_satellite_norad_id=satellite_norad_id,
                db=db,
                conflict_window_minutes=DEFAULT_PASSES_PER_SATELLITE
            )
            
            # If no conflicts found, this is our slot
            if not conflicts:
                logger.info(f"Found available slot at {current_time}")
                return current_time
            
            # Move to next time slot (skip by 30 minutes)
            current_time += timedelta(minutes=30)
            iteration += 1
        
        logger.warning(f"No available slot found within {search_hours_ahead} hours")
        return None
        
    except Exception as e:
        logger.error(f"Error finding available slot: {e}")
        return None


def optimize_schedule(db: Session) -> Dict[str, Any]:
    """
    Optimize the schedule by resolving conflicts and finding better time slots.
    
    Args:
        db: Database session
        
    Returns:
        Summary of optimization results
    """
    try:
        # Get all scheduled passes
        all_passes = db.query(PassSchedule).order_by(PassSchedule.start_time).all()
        
        conflicts_resolved = 0
        rescheduled_passes = 0
        
        for pass_schedule in all_passes:
            # Check for conflicts with this pass
            conflicts = check_temporal_conflicts(
                new_pass_start=pass_schedule.start_time,
                new_pass_end=pass_schedule.end_time,
                new_ground_station=pass_schedule.ground_station,
                new_satellite_norad_id=pass_schedule.satellite_norad_id,
                db=db
            )
            
            if conflicts:
                # Try to find a better time slot
                duration_minutes = (pass_schedule.end_time - pass_schedule.start_time).total_seconds() / 60
                
                new_start_time = find_next_available_slot(
                    requested_start=pass_schedule.start_time,
                    requested_duration_minutes=duration_minutes,
                    ground_station=pass_schedule.ground_station,
                    satellite_norad_id=pass_schedule.satellite_norad_id,
                    db=db
                )
                
                if new_start_time and new_start_time != pass_schedule.start_time:
                    # Update the pass schedule
                    pass_schedule.start_time = new_start_time
                    pass_schedule.end_time = new_start_time + timedelta(minutes=duration_minutes)
                    rescheduled_passes += 1
                    logger.info(f"Rescheduled pass {pass_schedule.pass_id} to {new_start_time}")
        
        # Commit changes
        db.commit()
        
        logger.info(f"Schedule optimization completed: {rescheduled_passes} passes rescheduled")
        
        return {
            "total_passes": len(all_passes),
            "conflicts_resolved": conflicts_resolved,
            "passes_rescheduled": rescheduled_passes,
            "optimization_status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Schedule optimization failed: {e}")
        db.rollback()
        return {"error": f"Schedule optimization failed: {e}"}


def validate_schedule_creation(
    satellite_norad_id: int,
    ground_station: str,
    start_time: datetime,
    end_time: datetime,
    db: Session
) -> Tuple[bool, List[ScheduleConflict]]:
    """
    Comprehensive validation for creating a new pass schedule.
    
    Args:
        satellite_norad_id: NORAD ID of the satellite
        ground_station: Ground station name
        start_time: Scheduled start time
        end_time: Scheduled end time
        db: Database session
        
    Returns:
        Tuple of (is_valid, list_of_conflicts)
    """
    try:
        # Check if satellite exists
        satellite = db.query(Satellite).filter(Satellite.norad_id == satellite_norad_id).first()
        if not satellite:
            return False, [ScheduleConflict(
                conflict_type=ConflictType.SATELLITE_ACCESS_CONFLICT,
                description=f"Satellite with NORAD ID {satellite_norad_id} not found in database",
                severity="high"
            )]
        
        # Check time validity
        if start_time >= end_time:
            return False, [ScheduleConflict(
                conflict_type=ConflictType.TEMPORAL_OVERLAP,
                description="Start time must be before end time",
                severity="high"
            )]
        
        # Check if start time is in the future
        if start_time <= datetime.now(timezone.utc):
            return False, [ScheduleConflict(
                conflict_type=ConflictType.TEMPORAL_OVERLAP,
                description="Start time must be in the future",
                severity="high"
            )]
        
        # Check for temporal conflicts
        conflicts = check_temporal_conflicts(
            new_pass_start=start_time,
            new_pass_end=end_time,
            new_ground_station=ground_station,
            new_satellite_norad_id=satellite_norad_id,
            db=db
        )
        
        # Schedule is valid if no high-severity conflicts
        high_severity_conflicts = [c for c in conflicts if c.severity == "high"]
        is_valid = len(high_severity_conflicts) == 0
        
        return is_valid, conflicts
        
    except Exception as e:
        logger.error(f"Schedule validation failed: {e}")
        return False, [ScheduleConflict(
            conflict_type=ConflictType.TEMPORAL_OVERLAP,
            description=f"Validation error: {str(e)}",
            severity="high"
        )]


def get_schedule_statistics(db: Session) -> Dict[str, Any]:
    """
    Get statistics about the current schedule state.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with schedule statistics
    """
    try:
        total_passes = db.query(PassSchedule).count()
        
        # Count passes by status
        status_counts = {}
        for status in ["scheduled", "active", "completed", "cancelled"]:
            count = db.query(PassSchedule).filter(PassSchedule.status == status).count()
            status_counts[status] = count
        
        # Count passes by ground station
        station_counts = {}
        stations = db.query(PassSchedule.ground_station).distinct().all()
        for station in stations:
            count = db.query(PassSchedule).filter(PassSchedule.ground_station == station[0]).count()
            station_counts[station[0]] = count
        
        # Count upcoming passes (next 24 hours)
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)
        upcoming_passes = db.query(PassSchedule).filter(
            and_(
                PassSchedule.start_time >= now,
                PassSchedule.start_time <= tomorrow
            )
        ).count()
        
        return {
            "total_passes": total_passes,
            "passes_by_status": status_counts,
            "passes_by_station": station_counts,
            "upcoming_passes_24h": upcoming_passes,
            "last_updated": now.isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Failed to get schedule statistics: {e}")
        return {"error": f"Failed to get statistics: {e}"}
