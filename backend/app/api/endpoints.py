from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.db.models import Satellite, TLE, PassSchedule

from app.services.tle_ingest import import_gp_group
from app.services.pass_generator import generate_sample_pass_schedules, generate_realistic_pass_data
from app.services.schedule_validator import validate_schedule_creation, get_schedule_statistics, optimize_schedule
from app.api.schemas import SatelliteOut, TLEOut, PassScheduleOut

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Hello World"}

@router.get("/health/db")
def check_database_connection(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify database connection.
    Returns success if database is accessible, error otherwise.
    """
    try:
        # Execute a simple query to test the connection
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {
            "status": "success",
            "message": "Database connection successful",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


@router.post("/tle/refresh")
def refresh_tle_data(group: str = "active", db: Session = Depends(get_db)):
    """
    Import live TLE data from Celestrak into the local database.

    - Uses the Celestrak GP TLE text API
    - Upserts satellites by NORAD ID
    - Inserts TLE rows for each object
    """
    try:
        summary = import_gp_group(db, group=group)
        return {
            "status": "success",
            "message": "TLE data imported successfully",
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing TLE data: {str(e)}"
        ) from e


@router.get("/satellites", response_model=List[SatelliteOut])
def get_all_satellites_with_related_data(db: Session = Depends(get_db)):
    """Get all satellites with their related TLE and PassSchedule data."""
    try:
        satellites = db.query(Satellite).options(
            joinedload(Satellite.tles),
            joinedload(Satellite.pass_schedules),
        ).all()

        return satellites
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching satellites: {str(e)}",
        )


@router.get("/satellites/{norad_id}", response_model=SatelliteOut)
def get_satellite_by_id(norad_id: int, db: Session = Depends(get_db)):
    """Get a single satellite by NORAD ID, including its TLEs and pass schedules."""
    satellite = (
        db.query(Satellite)
        .options(
            joinedload(Satellite.tles),
            joinedload(Satellite.pass_schedules),
        )
        .filter(Satellite.norad_id == norad_id)
        .one_or_none()
    )

    if satellite is None:
        raise HTTPException(status_code=404, detail="Satellite not found")

    return satellite


@router.get("/satellites/{norad_id}/tles", response_model=List[TLEOut])
def list_tles_for_satellite(norad_id: int, db: Session = Depends(get_db)):
    """List all TLEs for a given satellite (by NORAD ID), newest first."""
    exists = (
        db.query(Satellite.norad_id)
        .filter(Satellite.norad_id == norad_id)
        .scalar()
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Satellite not found")

    tles = (
        db.query(TLE)
        .filter(TLE.satellite_norad_id == norad_id)
        .order_by(TLE.timestamp.desc())
        .all()
    )

    return tles


@router.get("/satellites/{norad_id}/tles/latest", response_model=TLEOut)
def get_latest_tle_for_satellite(norad_id: int, db: Session = Depends(get_db)):
    """Get the most recent TLE for a given satellite (by NORAD ID)."""
    exists = (
        db.query(Satellite.norad_id)
        .filter(Satellite.norad_id == norad_id)
        .scalar()
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Satellite not found")

    tle = (
        db.query(TLE)
        .filter(TLE.satellite_norad_id == norad_id)
        .order_by(TLE.timestamp.desc())
        .first()
    )

    if tle is None:
        raise HTTPException(status_code=404, detail="No TLEs found for this satellite")

    return tle



@router.get("/pass-schedules", response_model=List[PassScheduleOut])
def list_pass_schedules(db: Session = Depends(get_db)):
    """List all scheduled passes with their associated satellite (by NORAD ID)."""
    schedules = db.query(PassSchedule).options(joinedload(PassSchedule.satellite)).all()

    # inject satellite_name for response schema
    for s in schedules:
        s.satellite_name = s.satellite.name if s.satellite else None

    return schedules



@router.post("/pass-schedules/generate")
def generate_pass_schedules(
    method: str = "sample",
    days_ahead: int = 7,
    db: Session = Depends(get_db)
):
    """
    Generate pass schedules for all satellites in the database.
    
    - method: "sample" for test data, "realistic" for orbital calculations
    - days_ahead: number of days to generate passes for
    """
    try:
        if method == "realistic":
            summary = generate_realistic_pass_data(db)
        else:
            summary = generate_sample_pass_schedules(db, days_ahead=days_ahead)
        
        return {
            "status": "success",
            "message": f"Generated pass schedules using {method} method",
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating pass schedules: {str(e)}"
        ) from e


@router.post("/pass-schedules/validate")
def validate_pass_schedule(
    satellite_norad_id: int,
    ground_station: str,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):
    """
    Validate a proposed pass schedule for temporal conflicts.
    
    - satellite_norad_id: NORAD catalog ID of the satellite
    - ground_station: Ground station name
    - start_time: Proposed start time (ISO format)
    - end_time: Proposed end time (ISO format)
    
    Returns validation results with any detected conflicts.
    """
    try:
        is_valid, conflicts = validate_schedule_creation(
            satellite_norad_id=satellite_norad_id,
            ground_station=ground_station,
            start_time=start_time,
            end_time=end_time,
            db=db
        )
        
        return {
            "is_valid": is_valid,
            "conflicts": [conflict.to_dict() for conflict in conflicts],
            "total_conflicts": len(conflicts),
            "high_severity_conflicts": len([c for c in conflicts if c.severity == "high"]),
            "validation_timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating pass schedule: {str(e)}"
        ) from e


@router.get("/schedule/statistics")
def get_schedule_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the current schedule state.
    
    Returns summary information about scheduled passes, conflicts, and system health.
    """
    try:
        stats = get_schedule_statistics(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting schedule statistics: {str(e)}"
        ) from e


@router.post("/schedule/optimize")
def optimize_current_schedule(db: Session = Depends(get_db)):
    """
    Optimize the current schedule by resolving conflicts and finding better time slots.
    
    Returns summary of optimization results.
    """
    try:
        result = optimize_schedule(db)
        return {
            "status": "success",
            "optimization_result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing schedule: {str(e)}"
        ) from e
