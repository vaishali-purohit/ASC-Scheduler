from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router
# Import models to ensure SQLAlchemy knows about them
from app.db import models  # noqa: F401
from app.db.session import engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASC Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
