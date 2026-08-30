from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..storage.fact_store import FactStore
from ..engine.evidence_engine import EvidenceAndConsistencyEngine

router = APIRouter(prefix="/api/conflicts", tags=["Conflicts & Evidence Engine"])

class ResolveConflictRequest(BaseModel):
    conflict_id: str
    chosen_record_id: str
    resolution_notes: str
    resolved_by: str = "Officer In-Charge"

@router.get("/list")
def list_all_conflicts(status: Optional[str] = None):
    store = FactStore()
    return store.list_conflicts(status=status)

@router.get("/anomalies")
def list_all_anomalies():
    store = FactStore()
    return store.list_anomalies()

@router.post("/trigger_evidence_engine")
def trigger_evidence_engine():
    engine = EvidenceAndConsistencyEngine()
    conflict_results = engine.process_consistency_and_conflicts()
    anomaly_results = engine.detect_and_explain_anomalies()
    return {
        "status": "success",
        "conflicts_processed": conflict_results,
        "anomalies_detected": anomaly_results
    }

@router.post("/resolve")
def resolve_conflict_manually(req: ResolveConflictRequest):
    store = FactStore()
    store.resolve_conflict(
        conflict_id=req.conflict_id,
        chosen_record_id=req.chosen_record_id,
        resolution_notes=req.resolution_notes,
        resolved_by=req.resolved_by
    )
    return {"status": "resolved", "conflict_id": req.conflict_id}
