#!/bin/bash
echo "Starting MineIntel Production Environment..."
cd backend
python seed_data.py
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
