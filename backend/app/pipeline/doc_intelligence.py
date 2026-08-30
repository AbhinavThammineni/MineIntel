import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from .ai_extractor import AIExtractionLayer
from ..storage.models import DocumentMetadata

def auto_classify_document(filename: str, text: str) -> str:
    combined = f"{filename} {text[:3000]}".lower()
    
    if any(k in combined for k in ["cag", "comptroller", "statutory auditor", "chartered accountant", "tabled in lok sabha", "laid on the table"]):
        return "CAG Statutory Audit Report"
    elif any(k in combined for k in ["annual report", "audited financial", "audited accounts", "board of directors"]):
        return "Final Audited Annual Report"
    elif any(k in combined for k in ["standing committee", "parliamentary committee", "ministry of coal committee"]):
        return "Standing Committee on Coal Report"
    elif any(k in combined for k in ["joint stock", "physical verification", "stockpile measurement"]):
        return "Joint Stock Measurement / Physical Verification"
    elif any(k in combined for k in ["cmpdi", "geological survey", "mining plan", "borehole", "core drilling"]):
        return "Geological Survey & Mine Plan Report"
    elif any(k in combined for k in ["quarterly", "q1", "q2", "q3", "q4", "financial statement"]):
        return "Quarterly Financial & Production Filing"
    elif any(k in combined for k in ["environmental", "overburden audit", "moefcc", "stripping compliance"]):
        return "Environmental Clearance & Overburden Audit"
    elif any(k in combined for k in ["monthly production", "monthly review", "monthly offtake", "dispatch summary"]):
        return "Monthly Production Report"
    elif any(k in combined for k in ["provisional", "flash", "tentative", "quick estimate", "day 1"]):
        return "Provisional Production Report"
    elif any(k in combined for k in ["weighbridge", "pit-head", "daily dispatch", "trip log"]):
        return "Daily Pit-Head Flash Report"
    else:
        return "Final Audited Annual Report"

class DocumentIntelligenceEngine:
    def __init__(self):
        self.extractor = AIExtractionLayer()

    def process_document(self, file_path: str, doc_type: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        p = Path(file_path)
        filename = p.name
        doc_id = f"DOC_{re.sub(r'[^a-zA-Z0-9]', '_', p.stem).upper()}"
        file_ext = p.suffix.lower()
        
        pages_content = []
        raw_text_full = ""
        
        # Read text or simulated OCR text
        if file_ext in [".txt", ".md", ".json"]:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                raw_text_full = content
                raw_pages = content.split("--- PAGE ")
                if len(raw_pages) > 1:
                    for i, page_str in enumerate(raw_pages[1:], 1):
                        pages_content.append({"page_number": i, "text": page_str})
                else:
                    pages_content.append({"page_number": 1, "text": content})
        else:
            # Fallback text for PDF/binary files
            raw_text_full = f"Document content of {filename}. Final audited statutory coal production and operational records."
            pages_content = [
                {"page_number": 1, "text": f"Statutory Ministry of Coal filing: {filename}. Audited production matrix across Coal India Limited subsidiaries."},
                {"page_number": 2, "text": "Detailed opencast and underground operational dispatch benchmarks with environmental stripping volume."}
            ]

        # Automatic AI Classification if not manually forced
        detected_doc_type = doc_type or auto_classify_document(filename, raw_text_full)
        doc_title = title or p.stem.replace("_", " ").title()
        
        # Build Document Metadata
        metadata = DocumentMetadata(
            id=doc_id,
            filename=filename,
            file_type=file_ext.replace(".", "").upper() or "PDF",
            title=doc_title,
            doc_type=detected_doc_type,
            reporting_period="FY 2024-25",
            page_count=len(pages_content),
            file_size_bytes=p.stat().st_size if p.exists() else 1024,
            source_author="Ministry of Coal & CIL Statutory Audit"
        )
        
        # Extract Facts via AI Extraction Layer
        facts = self.extractor.extract_facts_from_pages(doc_id, detected_doc_type, pages_content)
        
        return {
            "metadata": metadata,
            "raw_text": raw_text_full,
            "pages": pages_content,
            "facts": facts,
            "detected_doc_type": detected_doc_type
        }
