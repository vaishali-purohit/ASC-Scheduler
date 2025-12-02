# Automated Satellite Contact Scheduler (ASC-Scheduler)

This project aims to automate and visualize the critical process of scheduling communication windows with Low Earth Orbit (LEO) satellites, directly demonstrating skills in complex system design and Python-based algorithmic execution.

## System Stack

1. Backend & Core Logic: Python 3 (FastAPI)
2. Algorithmic Engine: pyorbital for orbital mechanics and pass prediction.
3. Data Persistence: PostgreSQL (Used for TLE history and optimized query performance).
4. Frontend & UI: React, TypeScript

## Features

### 1. Core Mission Engine (Python Backend)

- **Orbital Prediction API:** Implements a fast REST endpoint built with **Python (FastAPI)** to calculate satellite visibility schedules over any ground station.
- **Algorithmic Precision:** Integrates the industry-standard **SGP4/SDP4 model** (via `pyorbital`) to solve the complex mathematical problem of orbit prediction.
- **Data Ingestion Automation:** Automates fetching and updating the latest **TLE satellite data** from external sources, ensuring schedules are based on current orbital parameters.

### 2. Reliability & System Design (PostgreSQL)

- **Database Optimization:** Achieves low-latency queries by using a **compound index** in **PostgreSQL** to instantly find the next available contact time.
- **Schedule Validation:** Includes backend logic to check for **temporal conflicts** (collision avoidance) before a new command sequence is scheduled for execution.

### 3. Frontend & Monitoring (React)

- **Pass Schedule Dashboard:** A responsive **React/TypeScript** interface that clearly displays the upcoming satellite pass times and system status.
- **Professional Feedback:** Provides non-intrusive **modal notifications** for scheduling errors, giving the operator clear and actionable feedback.

## Project Structure

```
ASC-Scheduler/
├── backend/                    # Python/FastAPI/PostgreSQL logic
│   ├── app/                    # Main Python source directory
│   │   ├── api/                # API endpoints
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py   # Defines all FastAPI endpoints
│   │   ├── core/               # Core configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py      # Settings (DB URL, etc.)
│   │   ├── db/                 # Database connection and model management
│   │   │   ├── __init__.py
│   │   │   ├── session.py     # DB engine / session handling
│   │   │   └── models.py      # SQLAlchemy/ORM models and schema definition
│   │   └── main.py             # FastAPI application entry point
│   ├── tests/                  # Pytest unit tests
│   │   └── unit/
│   ├── requirements.txt        # Python dependencies
│   ├── README.md               # Backend Setup Guide
│   └── start_backend.sh        # Script to run the Python server
│
├── frontend/                   # React/TypeScript application
│   ├── public/                 # HTML, assets
│   ├── src/                    # Main React source directory
│   │   ├── components/        # Reusable UI components
│   │   │   └── PassScheduleTable.tsx
│   │   ├── pages/             # Main view components
│   │   │   └── Dashboard.tsx
│   │   ├── App.tsx
│   │   └── main.tsx           # Application entry point
│   ├── package.json           # Node dependencies
│   ├── README.md              # Frontend Setup Guide
│   └── start_frontend.sh      # Script to run the React development server
│
└── README.md                   # Main project documentation
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- pip and npm

### Backend Setup

See [backend/README.md](backend/README.md) for detailed instructions.

1. Navigate to backend directory
2. Create virtual environment
3. Install dependencies
4. Set up `.env` file with database credentials
5. Run the server

### Frontend Setup

See [frontend/README.md](frontend/README.md) for detailed instructions.

1. Navigate to frontend directory
2. Install dependencies
3. Run the development server

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health/db` - Database connection health check

### Satellites
- `GET /satellites` - Get all satellites with related TLE and PassSchedule data

## Development Status

✅ Backend API structure  
✅ Database models and relationships  
✅ Database connection  
✅ Basic CRUD endpoints (in progress)  
🚧 Frontend integration (in progress)  
🚧 Orbital prediction (planned)  
🚧 Pass scheduling (planned)
