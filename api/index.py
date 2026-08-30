import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Automatically seed facts on initial cold start
try:
    import seed_data
    seed_data.seed_all()
except Exception as e:
    print("Cold start seed notice:", e)

from app.main import app
