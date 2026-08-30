import sys
import os
import shutil
from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
DATA_DIR = Path("/tmp/mineintel_data")

# Configure environment for Vercel read-only serverless execution
os.environ["DATA_DIR"] = str(DATA_DIR)
os.environ["DB_PATH"] = str(DATA_DIR / "mineintel_facts.db")
os.environ["VECTOR_DB_PATH"] = str(DATA_DIR / "mineintel_vectors.json")
os.environ["GRAPH_DB_PATH"] = str(DATA_DIR / "mineintel_graph.json")

DATA_DIR.mkdir(exist_ok=True, parents=True)

# Copy bundled databases to writable /tmp
bundled_data_dir = BACKEND_DIR / "data"
if bundled_data_dir.exists():
    for f_name in ["mineintel_facts.db", "mineintel_vectors.json", "mineintel_graph.json"]:
        src = bundled_data_dir / f_name
        dst = DATA_DIR / f_name
        if src.exists() and not dst.exists():
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                print(f"Copy notice {f_name}: {e}")

# Add backend directory to sys.path
sys.path.insert(0, str(BACKEND_DIR))

# Ensure seed data exists
try:
    import seed_data
    db_file = DATA_DIR / "mineintel_facts.db"
    if not db_file.exists() or db_file.stat().st_size == 0:
        seed_data.seed_all()
except Exception as e:
    print("Seed initialization:", e)

from app.main import app
