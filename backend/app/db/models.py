from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .session import Base

# Model Definitions
class Satellite(Base):
    __tablename__ = "satellite"

    # Primary key is the NORAD catalog ID
    norad_id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    tles = relationship("TLE", back_populates="satellite", cascade="all, delete-orphan")
    pass_schedules = relationship("PassSchedule", back_populates="satellite", cascade="all, delete-orphan")


class TLE(Base):
    """Model for storing the satellite Two-Line Element (TLE) data."""

    __tablename__ = "tle"

    tle_id = Column(Integer, primary_key=True, index=True)
    satellite_norad_id = Column(Integer, ForeignKey("satellite.norad_id"), nullable=False) # e.g., 'ISS', 'GRUS-1'
    line1 = Column(String(80), nullable=False)
    line2 = Column(String(80), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    satellite = relationship("Satellite", back_populates="tles")

    # Index for fast TLE lookups by satellite and recency
    __table_args__ = (
        Index('idx_tle_satellite_timestamp', 'satellite_norad_id', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f"<TLE(tle_id={self.tle_id}, satellite_norad_id={self.satellite_norad_id})>"


class PassSchedule(Base):
    """Model for storing passes that have been scheduled for execution."""

    __tablename__ = "passschedule"

    pass_id = Column(Integer, primary_key=True, index=True)

    # Scheduling details
    satellite_norad_id = Column(Integer, ForeignKey("satellite.norad_id"), nullable=False)
    ground_station = Column(String(100), nullable=False)

    # Critical fields for optimization and conflict checking
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    status = Column(String(50), nullable=False)

    # Relationships
    satellite = relationship("Satellite", back_populates="pass_schedules")

    # Compound indexes for optimal query performance (as mentioned in README)
    __table_args__ = (
        # Primary schedule lookup index - for finding next available contact time
        Index('idx_pass_schedule_optimized', 'start_time', 'end_time', 'satellite_norad_id'),
        # Ground station scheduling index
        Index('idx_pass_schedule_station_time', 'ground_station', 'start_time'),
        # Status-based filtering index
        Index('idx_pass_schedule_status', 'status', 'start_time'),
        # Overlap detection index for conflict checking
        Index('idx_pass_schedule_overlap', 'start_time', 'end_time'),
    )

    def __repr__(self) -> str:
        return (
            f"<PassSchedule(pass_id={self.pass_id}, "
            f"satellite_norad_id={self.satellite_norad_id}, start={self.start_time})>"
        )
