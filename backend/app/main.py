from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .config import FRONTEND_DIR
from .api.routes_qa import router as qa_router
from .api.routes_gis import router as gis_router
from .api.routes_reports import router as reports_router
from .api.routes_parliament import router as parliament_router
from .api.routes_conflicts import router as conflicts_router
from .api.routes_ingest import router as ingest_router

app = FastAPI(
    title="MineIntel: Mining Intelligence & Evidence-Based Verification Platform",
    description="Enterprise API for mining document intelligence, evidence verification, GIS analytics, and parliamentary drafting.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(qa_router)
app.include_router(gis_router)
app.include_router(reports_router)
app.include_router(parliament_router)
app.include_router(conflicts_router)
app.include_router(ingest_router)

# Mount Static Frontend
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MineIntel Core",
        "version": "1.0.0",
        "databases": {
            "fact_store": "active",
            "vector_store": "active",
            "graph_store": "active"
        }
    }
