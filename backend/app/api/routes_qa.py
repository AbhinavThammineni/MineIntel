from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..engine.query_router import QueryRouter

router = APIRouter(prefix="/api/qa", tags=["Q&A"])

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    query_type: str
    answer: str
    citations: List[Dict[str, Any]]
    notes: Optional[List[str]] = []
    fact_data: Optional[Dict[str, Any]] = None
    table_data: Optional[List[Dict[str, Any]]] = None
    provenance_graph: Optional[Dict[str, Any]] = None

@router.post("/query", response_model=QueryResponse)
def ask_mineintel(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    router_engine = QueryRouter()
    result = router_engine.process_query(req.query)
    
    return QueryResponse(
        query=req.query,
        query_type=result.get("query_type", "exact_fact"),
        answer=result.get("answer", ""),
        citations=result.get("citations", []),
        notes=result.get("notes", []),
        fact_data=result.get("fact_data"),
        table_data=result.get("table_data"),
        provenance_graph=result.get("provenance_graph")
    )
