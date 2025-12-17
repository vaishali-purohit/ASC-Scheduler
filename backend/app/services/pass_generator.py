"""
Pass Schedule Generation Service - Simplified Working Implementation

This module provides functionality to generate realistic pass schedules for satellites
based on their TLE data and ground station locations using orbital mechanics.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Import pyorbital for orbital calculations
try:
    from pyorbital.orbital import Orbital
    PYORBITAL_AVAILABLE = True
except ImportError:
    PYORBITAL_AVAILABLE = False
    logging.warning("pyorbital not available. Install with: pip install pyorbital")

from sqlalchemy.orm import Session
from app.db.models import Satellite, TLE, PassSchedule

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

# Default ground station
DEFAULT_GROUND_STATION = {
    "name": os.getenv("DEFAULT_GROUND_STATION_NAME", "dummy"),
    "lat": os.getenv("DEFAULT_GROUND_STATION_LAT", "71"),
    "lon": os.getenv("DEFAULT_GROUND_STATION_LON", "116"),
    "alt": os.getenv("DEFAULT_GROUND_STATION_ALT", "1.070")
}

MIN_PASS_ELEVATION_DEGREES = os.getenv("MIN_PASS_ELEVATION_DEGREES", "1.0")
MAX_PASS_ELEVATION_DEGREES = os.getenv("MAX_PASS_ELEVATION_DEGREES", "5.0")

def get_latest_tle_for_satellite(db: Session, norad_id: str) -> Optional[Dict[str, str]]:
    """
    Get the latest TLE data for a satellite from the database.
    Returns dict with 'line1' and 'line2' keys, or None if not found.
    """
    try:
        satellite = db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
        if not satellite or not satellite.tles:
            return None
        
        # Get the most recent TLE
        latest_tle = max(satellite.tles, key=lambda t: t.timestamp)
        return {
            "line1": latest_tle.line1,
            "line2": latest_tle.line2
        }
    except Exception as e:
        logger.error(f"Failed to get TLE for satellite {norad_id}: {e}")
        return None


def calculate_satellite_passes(
    norad_id: str,
    tle_data: Dict[str, str],
    lat: float = DEFAULT_GROUND_STATION["lat"],
    lon: float = DEFAULT_GROUND_STATION["lon"],
    alt: float = DEFAULT_GROUND_STATION["alt"],
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    Calculate satellite passes using pyorbital.
    
    Args:
        norad_id: NORAD catalog ID of the satellite
        tle_data: Dict with 'line1' and 'line2' TLE data
        lat: Ground station latitude in degrees
        lon: Ground station longitude in degrees  
        alt: Ground station altitude in km
        count: Number of passes to calculate
        
    Returns:
        List of pass dictionaries with start_time, end_time, max_elevation, duration_minutes
    """
    if not PYORBITAL_AVAILABLE:
        logger.error("pyorbital not available. Cannot calculate passes.")
        return []
    
    try:
        # Initialize Orbital object with TLE data
        orb = Orbital(norad_id, line1=tle_data["line1"], line2=tle_data["line2"])
        
        # Get current UTC time
        start_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        
        # Calculate passes for next 48 hours (should be enough for multiple passes)
        length_hours = 48
        
        # Get next passes
        passes_data = orb.get_next_passes(start_time, length_hours, lon, lat, alt)
        
        if not passes_data:
            logger.warning(f"No passes calculated for satellite {norad_id}")
            return []
        
        processed_passes = []
        
        for i, pass_data in enumerate(passes_data[:count]):
            try:
                start_time_pass, end_time_pass, max_elevation_time = pass_data
                
                # Calculate maximum elevation at the peak time
                try:
                    azimuth, elevation = orb.get_observer_look(max_elevation_time, lon, lat, alt)
                    max_elevation = float(elevation)
                except Exception as e:
                    logger.warning(f"Could not calculate elevation for pass {i+1} of satellite {norad_id}: {e}")
                    max_elevation = MAX_PASS_ELEVATION_DEGREES
                
                # Only include passes above minimum elevation
                if max_elevation >= MIN_PASS_ELEVATION_DEGREES:
                    duration_seconds = (end_time_pass - start_time_pass).total_seconds()
                    
                    if duration_seconds > 0:
                        processed_passes.append({
                            "start_time": start_time_pass.isoformat() + "Z",
                            "end_time": end_time_pass.isoformat() + "Z",
                            "max_elevation": round(max_elevation, 2),
                            "duration_minutes": round(duration_seconds / 60, 1)
                        })
                        
            except Exception as e:
                logger.warning(f"Error processing pass {i+1} for satellite {norad_id}: {e}")
                continue
        
        logger.info(f"Calculated {len(processed_passes)} valid passes for satellite {norad_id}")
        return processed_passes
        
    except Exception as e:
        logger.error(f"Failed to calculate passes for satellite {norad_id}: {e}")
        return []


def generate_pass_schedules(db: Session, days_ahead: int = 7) -> Dict[str, Any]:
    """
    Generate pass schedules for all satellites in the database.
    Uses pyorbital to calculate realistic orbital passes.
    """
    if not PYORBITAL_AVAILABLE:
        return {"error": "pyorbital not available"}
    
    try:
        # Clear existing pass schedules
        logger.info("Clearing existing pass schedules...")
        deleted_count = db.query(PassSchedule).delete()
        logger.info(f"Deleted {deleted_count} existing pass schedules")
        
        # Get all satellites with TLE data
        satellites = db.query(Satellite).all()
        if not satellites:
            return {"error": "No satellites found in database"}
        
        logger.info(f"Processing {len(satellites)} satellites for pass schedule generation")
        
        schedules_created = 0
        satellites_processed = 0
        satellites_failed = 0
        
        for satellite in satellites:
            try:
                # Get TLE data for this satellite
                tle_data = get_latest_tle_for_satellite(db, str(satellite.norad_id))
                if not tle_data:
                    logger.warning(f"No TLE data found for satellite {satellite.norad_id}")
                    satellites_failed += 1
                    continue
                
                # Calculate passes for this satellite
                passes = calculate_satellite_passes(
                    norad_id=str(satellite.norad_id),
                    tle_data=tle_data,
                    count=3  # Generate 3 passes per satellite
                )
                
                # Create pass schedules in database
                for pass_data in passes:
                    try:
                        pass_schedule = PassSchedule(
                            satellite_norad_id=satellite.norad_id,
                            ground_station=DEFAULT_GROUND_STATION["name"],
                            start_time=datetime.fromisoformat(pass_data["start_time"].replace('Z', '+00:00')),
                            end_time=datetime.fromisoformat(pass_data["end_time"].replace('Z', '+00:00')),
                            status="scheduled"
                        )
                        db.add(pass_schedule)
                        schedules_created += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to create pass schedule for satellite {satellite.norad_id}: {e}")
                        continue
                
                satellites_processed += 1
                logger.info(f"Processed satellite {satellite.norad_id}: {len(passes)} passes generated")
                
            except Exception as e:
                logger.error(f"Failed to process satellite {satellite.norad_id}: {e}")
                satellites_failed += 1
                continue
        
        # Commit all changes
        db.commit()
        logger.info(f"Committed {schedules_created} pass schedules to database")
        
        # Verify final count
        final_count = db.query(PassSchedule).count()
        logger.info(f"Total pass schedules in database: {final_count}")
        
        return {
            "satellites_processed": satellites_processed,
            "satellites_failed": satellites_failed,
            "schedules_created": schedules_created,
            "calculation_method": "pyorbital",
            "ground_station": DEFAULT_GROUND_STATION["name"],
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate pass schedules: {e}")
        db.rollback()
        return {"error": f"Failed to generate pass schedules: {e}"}


def generate_sample_pass_schedules(db: Session, days_ahead: int = 7) -> Dict[str, Any]:
    """
    Generate sample pass schedules using pyorbital calculations.
    This is an alias for generate_pass_schedules for API compatibility.
    """
    return generate_pass_schedules(db, days_ahead)


def generate_realistic_pass_data(db: Session) -> Dict[str, Any]:
    """
    Generate realistic pass data using pyorbital calculations.
    This is an alias for generate_pass_schedules for API compatibility.
    """
    return generate_pass_schedules(db, 7)


def get_ground_stations_info() -> Dict[str, Any]:
    """
    Get information about available ground stations.
    """
    return {
        "total_stations": 1,
        "default_station": DEFAULT_GROUND_STATION["name"],
        "coordinates": {
            "latitude": DEFAULT_GROUND_STATION["lat"],
            "longitude": DEFAULT_GROUND_STATION["lon"],
            "elevation_km": DEFAULT_GROUND_STATION["alt"]
        }
    }


def update_all_tle_data(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Placeholder for automated TLE data updates.
    """
    return {
        "message": "TLE data update functionality not implemented",
        "timestamp": datetime.utcnow().isoformat()
    }


def refresh_ground_stations_cache() -> Dict[str, Any]:
    """
    Placeholder for ground stations cache refresh.
    """
    return {
        "message": "Ground stations cache refresh not implemented",
        "stations_count": 1
    }
