from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base

# Model Definitions
class Satellite(Base):
    __tablename__ = "satellite"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Relationships
    tles = relationship("TLE", back_populates="satellite", cascade="all, delete-orphan")
    pass_schedules = relationship("PassSchedule", back_populates="satellite", cascade="all, delete-orphan")

class TLE(Base):
    """
    Model for storing the satellite Two-Line Element (TLE) data.
    This supports the 'Data Ingestion Automation' feature.
    """
    __tablename__ = "tle"

    tle_id = Column(Integer, primary_key=True, index=True)
    satellite_id = Column(Integer, ForeignKey("satellite.id"), nullable=False) # e.g., 'ISS', 'GRUS-1'
    line1 = Column(String(80), nullable=False)
    line2 = Column(String(80), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    satellite = relationship("Satellite", back_populates="tles")

    def __repr__(self):
        return f"<TLE(tle_id={self.tle_id}, satellite_id={self.satellite_id})>"

class PassSchedule(Base):
    """
    Model for storing passes that have been scheduled for execution.
    This is essential for 'Schedule Validation' and 'Database Optimization'.
    """
    __tablename__ = "passschedule"

    pass_id = Column(Integer, primary_key=True, index=True)

    # Scheduling details
    satellite_id = Column(Integer, ForeignKey("satellite.id"), nullable=False)
    ground_station = Column(String(100), nullable=False)
    
    # Critical fields for optimization and conflict checking
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    status = Column(String(50), nullable=False)

    # Relationships
    satellite = relationship("Satellite", back_populates="pass_schedules")

    def __repr__(self):
        return f"<PassSchedule(pass_id={self.pass_id}, satellite_id={self.satellite_id}, start={self.start_time})>"
