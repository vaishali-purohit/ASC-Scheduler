from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from typing import List

from app.db.session import get_db
from app.db.models import Satellite, TLE, PassSchedule
from app.services.tle_ingest import import_gp_group

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


@router.get("/satellites", response_model=List[dict])
def get_all_satellites_with_related_data(db: Session = Depends(get_db)):
    """Get all satellites with their related TLE and PassSchedule data."""
    try:
        satellites = db.query(Satellite).options(
            joinedload(Satellite.tles),
            joinedload(Satellite.pass_schedules),
        ).all()

        result = []
        for satellite in satellites:
            satellite_data = {
                "norad_id": satellite.norad_id,
                "name": satellite.name,
                "description": satellite.description,
                "tles": [
                    {
                        "tle_id": tle.tle_id,
                        "line1": tle.line1,
                        "line2": tle.line2,
                        "timestamp": tle.timestamp.isoformat() if tle.timestamp else None,
                    }
                    for tle in satellite.tles
                ],
                "pass_schedules": [
                    {
                        "pass_id": schedule.pass_id,
                        "ground_station": schedule.ground_station,
                        "start_time": schedule.start_time.isoformat()
                        if schedule.start_time
                        else None,
                        "end_time": schedule.end_time.isoformat()
                        if schedule.end_time
                        else None,
                        "status": schedule.status,
                    }
                    for schedule in satellite.pass_schedules
                ],
            }
            result.append(satellite_data)

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching satellites: {str(e)}",
        )


@router.get("/satellites/{norad_id}", response_model=dict)
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

    return {
        "norad_id": satellite.norad_id,
        "name": satellite.name,
        "description": satellite.description,
        "tles": [
            {
                "tle_id": tle.tle_id,
                "line1": tle.line1,
                "line2": tle.line2,
                "timestamp": tle.timestamp.isoformat() if tle.timestamp else None,
            }
            for tle in satellite.tles
        ],
        "pass_schedules": [
            {
                "pass_id": schedule.pass_id,
                "ground_station": schedule.ground_station,
                "start_time": schedule.start_time.isoformat()
                if schedule.start_time
                else None,
                "end_time": schedule.end_time.isoformat()
                if schedule.end_time
                else None,
                "status": schedule.status,
            }
            for schedule in satellite.pass_schedules
        ],
    }


@router.get("/satellites/{norad_id}/tles", response_model=List[dict])
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

    return [
        {
            "tle_id": tle.tle_id,
            "line1": tle.line1,
            "line2": tle.line2,
            "timestamp": tle.timestamp.isoformat() if tle.timestamp else None,
        }
        for tle in tles
    ]


@router.get("/satellites/{norad_id}/tles/latest", response_model=dict)
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

    return {
        "tle_id": tle.tle_id,
        "line1": tle.line1,
        "line2": tle.line2,
        "timestamp": tle.timestamp.isoformat() if tle.timestamp else None,
    }


@router.get("/pass-schedules", response_model=List[dict])
def list_pass_schedules(db: Session = Depends(get_db)):
    """List all scheduled passes with their associated satellite (by NORAD ID)."""
    schedules = db.query(PassSchedule).options(joinedload(PassSchedule.satellite)).all()

    return [
        {
            "pass_id": s.pass_id,
            "satellite_norad_id": s.satellite_norad_id,
            "satellite_name": s.satellite.name if s.satellite else None,
            "ground_station": s.ground_station,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "status": s.status,
        }
        for s in schedules
    ]
