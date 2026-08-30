import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from .ai_extractor import AIExtractionLayer
from ..storage.models import DocumentMetadata

class DocumentIntelligenceEngine:
    def __init__(self):
        self.extractor = AIExtractionLayer()

    def process_document(self, file_path: str, doc_type: str = "Audited Annual Report", title: Optional[str] = None) -> Dict[str, Any]:
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
                # Split by page marker if available or by paragraph
                raw_pages = content.split("--- PAGE ")
                if len(raw_pages) > 1:
                    for i, page_str in enumerate(raw_pages[1:], start=1):
                        pages_content.append({"page_number": i, "text": page_str})
                else:
                    pages_content.append({"page_number": 1, "text": content})
        else:
            # Fallback plain text reading
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    raw_text_full = content
                    pages_content.append({"page_number": 1, "text": content})
            except Exception:
                raw_text_full = f"Scanned Mining Record: {filename}"
                pages_content.append({"page_number": 1, "text": raw_text_full})
                
        # Extract structured facts from all pages
        all_extracted_facts = []
        for page in pages_content:
            p_num = page["page_number"]
            p_text = page["text"]
            
            # Check for tables
            facts_from_text = self.extractor.extract_structured_facts_from_text(p_text, doc_id, doc_type, p_num)
            all_extracted_facts.extend(facts_from_text)
            
        doc_meta = DocumentMetadata(
            id=doc_id,
            filename=filename,
            file_type=file_ext.replace(".", ""),
            title=title or p.stem.replace("_", " ").title(),
            doc_type=doc_type,
            page_count=len(pages_content),
            file_size_bytes=p.stat().st_size if p.exists() else len(raw_text_full)
        )
        
        return {
            "metadata": doc_meta,
            "pages": pages_content,
            "facts": all_extracted_facts,
            "raw_text": raw_text_full
        }
