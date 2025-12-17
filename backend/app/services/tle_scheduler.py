"""
Automated TLE Update Service

This module provides functionality for automated TLE data updates using background tasks,
ensuring satellite orbital data remains current without manual intervention.
"""

import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.services.tle_ingest import import_gp_group
from app.db.models import Satellite, TLE
from app.db.session import SessionLocal

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class TLEUpdateManager:
    """
    Manages automated TLE updates using APScheduler for background task execution.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.update_config = {
            "active_satellites": {"group": "active", "interval_hours": 6},
            "starlink": {"group": "starlink", "interval_hours": 12},
            "weather": {"group": "noaa", "interval_hours": 8}
        }
    
    async def start_scheduler(self):
        """Start the background scheduler for TLE updates."""
        if self.is_running:
            logger.warning("TLE update scheduler is already running")
            return
        
        try:
            # Add scheduled jobs for different satellite groups
            await self._schedule_update_jobs()
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("TLE update scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start TLE update scheduler: {e}")
            raise
    
    async def stop_scheduler(self):
        """Stop the background scheduler."""
        if not self.is_running:
            logger.warning("TLE update scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("TLE update scheduler stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop TLE update scheduler: {e}")
    
    async def _schedule_update_jobs(self):
        """Schedule individual TLE update jobs for different satellite groups."""
        
        # Schedule active satellites update every 6 hours
        self.scheduler.add_job(
            func=self._update_satellite_group,
            trigger=CronTrigger(minute=0, hour="*/6"),  # Every 6 hours
            args=["active"],
            id="update_active_satellites",
            name="Update Active Satellites TLE Data",
            max_instances=1,  # Prevent overlapping executions
            coalesce=True,    # Combine missed executions
            misfire_grace_time=3600  # Allow 1 hour grace period
        )
        
        # Schedule Starlink satellites update every 12 hours
        self.scheduler.add_job(
            func=self._update_satellite_group,
            trigger=CronTrigger(minute=30, hour="*/12"),  # Every 12 hours
            args=["starlink"],
            id="update_starlink_satellites",
            name="Update Starlink Satellites TLE Data",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=7200  # Allow 2 hours grace period
        )
        
        # Schedule weather satellites update every 8 hours
        self.scheduler.add_job(
            func=self._update_satellite_group,
            trigger=CronTrigger(minute=15, hour="*/8"),  # Every 8 hours
            args=["weather"],
            id="update_weather_satellites",
            name="Update Weather Satellites TLE Data",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=5400  # Allow 1.5 hours grace period
        )
        
        logger.info(f"Scheduled {len(self.scheduler.get_jobs())} TLE update jobs")
    
    async def _update_satellite_group(self, group: str):
        """Background task to update TLE data for a specific satellite group."""
        db = None
        try:
            # Create database session
            db = SessionLocal()
            
            logger.info(f"Starting TLE update for satellite group: {group}")
            
            # Get update summary
            summary = import_gp_group(db, group=group)
            
            logger.info(f"TLE update completed for group '{group}': {summary}")
            
            # Log update statistics
            if summary.get("tles_inserted", 0) > 0:
                logger.info(f"Successfully updated {summary['tles_inserted']} TLE records for {group} satellites")
            
            if summary.get("satellites_created", 0) > 0:
                logger.info(f"Added {summary['satellites_created']} new satellites to the database")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to update TLE data for group '{group}': {e}")
            return {"error": str(e)}
            
        finally:
            if db:
                db.close()
    
    async def trigger_manual_update(self, groups: list = None) -> Dict[str, Any]:
        """
        Manually trigger TLE updates for specified groups or all configured groups.
        
        Args:
            groups: List of satellite groups to update. If None, updates all groups.
            
        Returns:
            Dictionary with update results for each group
        """
        if groups is None:
            groups = list(self.update_config.keys())
        
        results = {}
        
        for group in groups:
            if group not in self.update_config:
                logger.warning(f"Unknown satellite group: {group}")
                results[group] = {"error": "Unknown satellite group"}
                continue
            
            try:
                logger.info(f"Manually triggering TLE update for group: {group}")
                result = await self._update_satellite_group(group)
                results[group] = result
                
            except Exception as e:
                logger.error(f"Manual TLE update failed for group '{group}': {e}")
                results[group] = {"error": str(e)}
        
        return results
    
    def get_update_status(self) -> Dict[str, Any]:
        """
        Get current status of the TLE update system.
        
        Returns:
            Dictionary with scheduler status and next update times
        """
        if not self.is_running:
            return {
                "scheduler_running": False,
                "message": "TLE update scheduler is not running"
            }
        
        jobs = self.scheduler.get_jobs()
        job_status = {}
        
        for job in jobs:
            job_status[job.id] = {
                "name": job.name,
                "next_run": job.next_run_time.isoformat() + "Z" if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
        
        return {
            "scheduler_running": True,
            "total_jobs": len(jobs),
            "jobs": job_status,
            "last_updated": datetime.now(timezone.utc).isoformat() + "Z"
        }
    
    def get_update_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get statistics about TLE data freshness and update history.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with TLE update statistics
        """
        try:
            # Count total satellites
            total_satellites = db.query(Satellite).count()
            
            # Count total TLE records
            total_tles = db.query(TLE).count()
            
            # Get TLE freshness statistics
            now = datetime.now(timezone.utc)
            freshness_stats = {}
            
            time_ranges = [
                ("last_24h", now - timedelta(hours=24)),
                ("last_3d", now - timedelta(days=3)),
                ("last_7d", now - timedelta(days=7)),
                ("older_than_7d", now - timedelta(days=7))
            ]
            
            for range_name, cutoff_time in time_ranges:
                if range_name == "older_than_7d":
                    count = db.query(TLE).filter(TLE.timestamp < cutoff_time).count()
                else:
                    count = db.query(TLE).filter(TLE.timestamp >= cutoff_time).count()
                freshness_stats[range_name] = count
            
            # Get satellites with recent TLE data
            recent_tle_satellites = db.query(Satellite).join(TLE).filter(
                TLE.timestamp >= now - timedelta(days=3)
            ).distinct().count()
            
            # Calculate data freshness percentage
            satellites_with_recent_data = db.query(Satellite).join(TLE).filter(
                TLE.timestamp >= now - timedelta(days=7)
            ).distinct().count()
            
            freshness_percentage = (satellites_with_recent_data / total_satellites * 100) if total_satellites > 0 else 0
            
            return {
                "total_satellites": total_satellites,
                "total_tle_records": total_tles,
                "satellites_with_recent_data_3d": recent_tle_satellites,
                "freshness_percentage_7d": round(freshness_percentage, 2),
                "tle_freshness_stats": freshness_stats,
                "last_updated": now.isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Failed to get update statistics: {e}")
            return {"error": f"Failed to get statistics: {e}"}


# Global instance for use across the application
tle_update_manager = TLEUpdateManager()


async def start_tle_updates():
    """Start the TLE update system."""
    await tle_update_manager.start_scheduler()


async def stop_tle_updates():
    """Stop the TLE update system."""
    await tle_update_manager.stop_scheduler()


async def trigger_tle_update(groups: list = None):
    """Trigger manual TLE updates."""
    return await tle_update_manager.trigger_manual_update(groups)


def get_tle_update_status():
    """Get TLE update system status."""
    return tle_update_manager.get_update_status()


def get_tle_statistics(db: Session):
    """Get TLE update statistics."""
    return tle_update_manager.get_update_statistics(db)
