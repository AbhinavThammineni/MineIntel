from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

class BoundingBox(BaseModel):
    x0: float = 0.0
    y0: float = 0.0
    x1: float = 100.0
    y1: float = 50.0

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    file_type: str
    title: str
    doc_type: str  # Provisional, Audited Annual Report, Monthly Dispatch, Geological Report
    reporting_period: Optional[str] = None
    upload_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    page_count: int = 1
    file_size_bytes: int = 0
    source_author: Optional[str] = None

class DocumentChunk(BaseModel):
    id: str
    doc_id: str
    page_number: int
    text: str
    bbox: Optional[BoundingBox] = None
    section_title: Optional[str] = None
    embedding: Optional[List[float]] = None

class MineEntity(BaseModel):
    id: str
    code: str
    name: str
    normalized_name: str
    subsidiary: str  # BCCL, CCL, ECL, SECL, MCL, WCL, NCL, CMPDI
    state: str
    district: str
    lat: float
    lng: float
    mine_type: str = "Opencast"  # Opencast, Underground, Mixed
    operational_status: str = "Active"

class FactRecord(BaseModel):
    id: Optional[str] = None
    doc_id: str
    doc_type: str
    page_number: int = 1
    bbox: Optional[Dict[str, float]] = None
    raw_text: Optional[str] = None
    
    mine_code: str
    mine_name: str
    subsidiary: str
    metric: str  # Coal Production, Overburden Removal, Coal Dispatch, Coal Reserves, Manpower
    
    raw_value: float
    raw_unit: str
    normalized_value: float
    normalized_unit: str  # MT for Coal, MCuM for Overburden, Count for Manpower
    
    fiscal_year: str  # e.g. "2023-24", "2023"
    period_type: str = "Annual"  # Annual, Provisional, Monthly
    
    is_superseded: bool = False
    superseded_by: Optional[str] = None
    supersession_reason: Optional[str] = None
    has_conflict: bool = False
    conflict_id: Optional[str] = None
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DataConflict(BaseModel):
    id: str
    conflict_type: str  # genuine_conflict, superseded_discrepancy, unit_mismatch
    mine_code: str
    mine_name: str
    metric: str
    fiscal_year: str
    records_involved: List[Dict[str, Any]]
    discrepancy_delta: float
    status: str = "detected"  # detected, superseded, resolved, under_review
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AnomalyRecord(BaseModel):
    id: str
    mine_code: str
    mine_name: str
    subsidiary: str
    metric: str
    fiscal_year: str
    current_value: float
    historical_avg: float
    deviation_pct: float
    anomaly_type: str  # steep_growth, steep_decline, outlier
    explanation: Optional[str] = None
    supporting_doc_id: Optional[str] = None
    supporting_page: Optional[int] = None
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ParliamentaryDraft(BaseModel):
    id: str
    question_no: str
    session: str  # Monsoon Session 2024, Budget Session 2025
    house: str = "Lok Sabha"  # Lok Sabha / Rajya Sabha
    ministry: str = "Ministry of Coal"
    question_text: str
    key_entities: List[str]
    time_period: str
    drafted_response: str
    annexure_table: List[Dict[str, Any]]
    confidence_score: float = 0.98
    evidence_sources: List[Dict[str, Any]]
    approval_status: str = "Draft"  # Draft, Reviewed, Approved, Rejected
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
