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
