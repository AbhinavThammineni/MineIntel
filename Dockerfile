# Production Multi-Stage Dockerfile for MineIntel
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     curl     && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend /app/backend
COPY frontend /app/frontend
COPY sample_data /app/sample_data

# Set working directory to backend
WORKDIR /app/backend

# Seed database on initial startup if not present
RUN python seed_data.py

EXPOSE 8000

# Start production server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
