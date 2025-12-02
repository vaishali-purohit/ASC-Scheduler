from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the SQLAlchemy engine
# pool_pre_ping=True helps handle dropped connections, improving reliability
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Create a SessionLocal class to get a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model definitions
Base = declarative_base()

# Dependency to get a database session (used by FastAPI endpoints)
def get_db():
    """Provides a database session for a single request (Dependency Injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
