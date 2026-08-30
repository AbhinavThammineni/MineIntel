from fastapi import APIRouter, UploadFile, File, Form
from typing import Dict, Any, Optional
import shutil
from pathlib import Path
from ..config import DOCUMENTS_DIR
from ..pipeline.doc_intelligence import DocumentIntelligenceEngine
from ..storage.fact_store import FactStore
from ..storage.vector_store import VectorStore
from ..storage.graph_store import MiningGraphStore
from ..engine.evidence_engine import EvidenceAndConsistencyEngine
from ..storage.models import FactRecord

router = APIRouter(prefix="/api/ingest", tags=["Document Ingestion"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None),
    title: Optional[str] = Form(None)
):
    save_path = DOCUMENTS_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc_engine = DocumentIntelligenceEngine()
    processed = doc_engine.process_document(str(save_path), doc_type=doc_type, title=title)
    
    fact_store = FactStore()
    vector_store = VectorStore()
    graph_store = MiningGraphStore()
    
    # 1. Save Document
    doc_meta = processed["metadata"]
    fact_store.add_document(doc_meta, raw_content=processed["raw_text"])
    
    # 2. Save Vector Chunks
    for page in processed["pages"]:
        vector_store.add_chunk(
            doc_id=doc_meta.id,
            page_number=page["page_number"],
            text=page["text"],
            section=doc_meta.title
        )
        
    # 3. Save Structured Facts
    saved_fact_ids = []
    for f in processed["facts"]:
        fact_obj = FactRecord(**f)
        fid = fact_store.add_fact(fact_obj)
        saved_fact_ids.append(fid)
        
    # 4. Trigger Evidence Engine
    evidence_engine = EvidenceAndConsistencyEngine(fact_store, vector_store)
    evidence_engine.process_consistency_and_conflicts()
    evidence_engine.detect_and_explain_anomalies()
    
    # 5. Update Graph
    mines = fact_store.get_all_mines()
    all_facts = fact_store.query_facts(include_superseded=True)
    graph_store.populate_from_facts(mines, all_facts)
    
    return {
        "status": "success",
        "doc_id": doc_meta.id,
        "filename": doc_meta.filename,
        "auto_detected_doc_type": processed["detected_doc_type"],
        "facts_extracted_count": len(saved_fact_ids),
        "facts": processed["facts"]
    }

@router.get("/documents")
def list_ingested_documents():
    store = FactStore()
    return store.list_documents()
