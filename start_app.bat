@echo off

REM Start API Management System

REM 1. Stop any existing Docker Compose containers
echo Stopping existing Docker Compose containers...
docker-compose down

REM 2. Start Docker Compose (PostgreSQL)
echo Starting Docker Compose...
docker-compose up -d

REM 3. Wait for PostgreSQL to initialize
echo Waiting for PostgreSQL to initialize...
timeout /t 15 /nobreak > NUL

REM 4. Start FastAPI application on port 8081
echo Starting FastAPI application...
python -m uvicorn main:app --host 0.0.0.0 --port 8080
