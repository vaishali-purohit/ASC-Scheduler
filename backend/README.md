# Backend Setup Guide

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation Steps

### 1. Create Virtual Environment

```bash
python -m venv .venv
# or
python3 -m venv .venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**

```bash
source .venv/bin/activate
```

**On Windows:**

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE asc_scheduler;

# Exit psql
\q
```

#### Create `.env` File

Create a `.env` file in the `backend/` directory with the following content:

```env
DB_USERNAME=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOSTNAME=localhost
DB_PORT=5432
DB_NAME=asc_scheduler
CELESTRAK_API_URL=your_data_link_url
```

Replace the values with your actual PostgreSQL credentials.

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

Or use the provided script:

```bash
./start_backend.sh
```

## Verification

Once the server is running:

- **Root endpoint**: Open http://127.0.0.1:8000/ in browser -> should see `{"message": "Hello World"}`
- **API Documentation**: Open http://127.0.0.1:8000/docs -> see FastAPI Swagger UI
- **Health Check**: Open http://127.0.0.1:8000/health/db -> verify database connection

## Database Schema

### Database Name

`asc_scheduler`

### Tables

#### 1. `satellite`

Stores satellite information.

| Column      | Type                   | Constraints           |
| ----------- | ---------------------- | --------------------- |
| norad_id    | integer                | PRIMARY KEY, NOT NULL |
| name        | character varying(100) | NOT NULL              |
| description | text                   | NULLABLE              |

#### 2. `tle`

Stores Two-Line Element (TLE) data for satellites.

| Column             | Type                     | Constraints           |
| ------------------ | ------------------------ | --------------------- |
| tle_id             | integer                  | PRIMARY KEY, NOT NULL |
| satellite_norad_id | integer                  | FOREIGN KEY, NOT NULL |
| line1              | character varying(80)    | NOT NULL              |
| line2              | character varying(80)    | NOT NULL              |
| timestamp          | timestamp with time zone | NOT NULL              |

#### 3. `passschedule`

Stores scheduled satellite passes.

| Column             | Type                     | Constraints           |
| ------------------ | ------------------------ | --------------------- |
| pass_id            | integer                  | PRIMARY KEY, NOT NULL |
| satellite_norad_id | integer                  | FOREIGN KEY, NOT NULL |
| ground_station     | character varying(100)   | NOT NULL              |
| start_time         | timestamp with time zone | NOT NULL              |
| end_time           | timestamp with time zone | NOT NULL              |
| status             | character varying(50)    | NOT NULL              |

## Data Link

- [Celestrak TLE Data](https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle)

## API Endpoints

### Health & Status

- `GET /` - Root endpoint
- `GET /health/db` - Database connection health check

### Satellites

- `GET /satellites` - Get all satellites with related TLE and PassSchedule data

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints.py      # API route definitions
│   ├── core/
│   │   └── config.py         # Configuration and settings
│   ├── db/
│   │   ├── models.py         # SQLAlchemy models
│   │   └── session.py         # Database session management
│   └── main.py               # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```
