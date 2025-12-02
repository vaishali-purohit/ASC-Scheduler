from fastapi import FastAPI
from app.api.endpoints import router
# Import models to ensure SQLAlchemy knows about them
from app.db import models  # noqa: F401

app = FastAPI(title="ASC Scheduler API")

app.include_router(router)
