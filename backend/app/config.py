import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _load_env():
    """Load environment variables from backend/.env or root .env if present."""
    candidates = [
        BASE_DIR / ".env",
        BASE_DIR.parent / ".env"
    ]
    for env_path in candidates:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
                break
            except Exception:
                pass

_load_env()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Detect Vercel / Read-Only Serverless Environment
IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

if IS_VERCEL:
    DATA_DIR = Path("/tmp/mineintel_data")
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    
    # Copy pre-packaged seed data to writable /tmp if not already present
    bundled_data_dir = BASE_DIR / "data"
    if bundled_data_dir.exists():
        for filename in ["mineintel_facts.db", "mineintel_vectors.json", "mineintel_graph.json"]:
            src_f = bundled_data_dir / filename
            dst_f = DATA_DIR / filename
            if src_f.exists() and not dst_f.exists():
                try:
                    shutil.copy2(src_f, dst_f)
                except Exception as e:
                    print(f"Notice: Failed to copy {filename} to /tmp: {e}")
else:
    DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
    try:
        DATA_DIR.mkdir(exist_ok=True, parents=True)
    except Exception:
        DATA_DIR = Path("/tmp/mineintel_data")
        DATA_DIR.mkdir(exist_ok=True, parents=True)

DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "mineintel_facts.db"))
VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", DATA_DIR / "mineintel_vectors.json"))
GRAPH_DB_PATH = Path(os.getenv("GRAPH_DB_PATH", DATA_DIR / "mineintel_graph.json"))
DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", DATA_DIR / "documents"))
try:
    DOCUMENTS_DIR.mkdir(exist_ok=True, parents=True)
except Exception:
    pass

FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", BASE_DIR.parent / "frontend"))
