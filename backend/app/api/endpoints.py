from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from typing import List
from app.db.session import get_db
from app.db.models import Satellite

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

@router.get("/satellites", response_model=List[dict])
def get_all_satellites_with_related_data(db: Session = Depends(get_db)):
    """
    Get all satellites with their related TLE and PassSchedule data.
    Returns a list of satellites with joined data from all tables.
    """
    try:
        # Query all satellites with eager loading of related data
        satellites = db.query(Satellite).options(
            joinedload(Satellite.tles),
            joinedload(Satellite.pass_schedules)
        ).all()
        
        # Format the response with all related data
        result = []
        for satellite in satellites:
            satellite_data = {
                "id": satellite.id,
                "name": satellite.name,
                "description": satellite.description,
                "tles": [
                    {
                        "tle_id": tle.tle_id,
                        "line1": tle.line1,
                        "line2": tle.line2,
                        "timestamp": tle.timestamp.isoformat() if tle.timestamp else None
                    }
                    for tle in satellite.tles
                ],
                "pass_schedules": [
                    {
                        "pass_id": schedule.pass_id,
                        "ground_station": schedule.ground_station,
                        "start_time": schedule.start_time.isoformat() if schedule.start_time else None,
                        "end_time": schedule.end_time.isoformat() if schedule.end_time else None,
                        "status": schedule.status
                    }
                    for schedule in satellite.pass_schedules
                ]
            }
            result.append(satellite_data)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching satellites: {str(e)}"
        )
