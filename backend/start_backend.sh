#!/bin/bash
echo "Starting ASC-Scheduler Python Backend (FastAPI) on port 8000..."

# Create and activate virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies (only installs new ones if already run)
pip install -r requirements.txt


# Run the FastAPI application
# The --host 0.0.0.0 ensures it's accessible from the frontend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
