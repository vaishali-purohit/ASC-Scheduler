from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TLEOut(BaseModel):
    tle_id: int
    line1: str
    line2: str
    timestamp: Optional[datetime]

    class Config:
        orm_mode = True


class PassScheduleOut(BaseModel):
    pass_id: int
    satellite_norad_id: int
    satellite_name: Optional[str] = None
    ground_station: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    status: str

    class Config:
        orm_mode = True


class SatelliteOut(BaseModel):
    norad_id: int
    name: str
    description: Optional[str] = None
    tles: List[TLEOut]
    pass_schedules: List[PassScheduleOut]

    class Config:
        orm_mode = True
