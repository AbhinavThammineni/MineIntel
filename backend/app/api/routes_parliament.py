from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from ..storage.fact_store import FactStore
from ..storage.models import ParliamentaryDraft
from ..engine.query_router import QueryRouter

router = APIRouter(prefix="/api/parliament", tags=["Parliamentary Drafts"])

class GenerateDraftRequest(BaseModel):
    question_no: str
    session: str = "Monsoon Session 2024"
    house: str = "Lok Sabha"
    question_text: str

class UpdateApprovalRequest(BaseModel):
    draft_id: str
    approval_status: str
    approved_by: str
    notes: Optional[str] = None

@router.post("/draft")
def generate_parliamentary_draft(req: GenerateDraftRequest):
    router_engine = QueryRouter()
    store = FactStore()
    
    result = router_engine.process_query(f"parliamentary draft {req.question_text}")
    draft_id = f"PARL_DRAFT_{uuid.uuid4().hex[:8].upper()}"
    
    draft_obj = ParliamentaryDraft(
        id=draft_id,
        question_no=req.question_no,
        session=req.session,
        house=req.house,
        ministry="Ministry of Coal",
        question_text=req.question_text,
        key_entities=["Coal India Limited", "BCCL", "CCL", "ECL", "SECL", "MCL", "WCL", "NCL"],
        time_period="2021-22 to 2024-25",
        drafted_response=result.get("answer", ""),
        annexure_table=result.get("annexure", []),
        confidence_score=0.99,
        evidence_sources=result.get("citations", []),
        approval_status="Draft"
    )
    
    store.save_parliamentary_draft(draft_obj)
    return draft_obj

@router.get("/list")
def list_drafts():
    store = FactStore()
    return store.list_parliamentary_drafts()

@router.post("/approve")
def approve_draft(req: UpdateApprovalRequest):
    store = FactStore()
    with store.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE parliamentary_drafts SET approval_status = ?, approved_by = ?, approved_at = ? WHERE id = ?",
            (req.approval_status, req.approved_by, datetime.utcnow().isoformat(), req.draft_id)
        )
        conn.commit()
    return {"status": "success", "draft_id": req.draft_id, "approval_status": req.approval_status}
