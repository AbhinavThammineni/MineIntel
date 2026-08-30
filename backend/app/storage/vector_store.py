import json
import re
import math
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..config import VECTOR_DB_PATH

class VectorStore:
    def __init__(self, storage_path=None):
        self.storage_path = Path(storage_path or VECTOR_DB_PATH)
        self.chunks: List[Dict[str, Any]] = []
        self.load()

    def load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception:
                self.chunks = []
        else:
            self.chunks = []

    def save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2)

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]+\b', text)]

    def _compute_sparse_embedding(self, text: str) -> Dict[str, float]:
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        counts = {}
        for t in tokens:
            counts[t] = counts.get(t, 0) + 1
        
        # Normalize vector to unit length
        norm = math.sqrt(sum(v * v for v in counts.values()))
        return {k: v / norm for k, v in counts.items()} if norm > 0 else {}

    def add_chunk(self, doc_id: str, page_number: int, text: str, bbox: Optional[Dict[str, float]] = None, section: str = "", metadata: Optional[Dict[str, Any]] = None) -> str:
        chunk_id = f"{doc_id}_p{page_number}_{len(self.chunks)+1}"
        vec = self._compute_sparse_embedding(text)
        
        chunk = {
            "id": chunk_id,
            "doc_id": doc_id,
            "page_number": page_number,
            "text": text,
            "bbox": bbox or {"x0": 50.0, "y0": 100.0, "x1": 500.0, "y1": 150.0},
            "section": section,
            "metadata": metadata or {},
            "vector": vec
        }
        self.chunks.append(chunk)
        self.save()
        return chunk_id

    def search(self, query: str, top_k: int = 5, doc_id_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        q_vec = self._compute_sparse_embedding(query)
        if not q_vec:
            return []

        results = []
        for chunk in self.chunks:
            if doc_id_filter and chunk.get("doc_id") != doc_id_filter:
                continue

            c_vec = chunk.get("vector", {})
            # Dot product for cosine similarity
            score = sum(q_vec[k] * c_vec[k] for k in q_vec if k in c_vec)
            
            # Boost score if exact keywords match
            q_lower = query.lower()
            text_lower = chunk.get("text", "").lower()
            for token in q_vec:
                if token in text_lower and len(token) > 3:
                    score += 0.05
                    
            if score > 0.05:
                results.append({
                    "id": chunk["id"],
                    "doc_id": chunk["doc_id"],
                    "page_number": chunk["page_number"],
                    "text": chunk["text"],
                    "bbox": chunk.get("bbox", {}),
                    "section": chunk.get("section", ""),
                    "score": round(score, 4)
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def find_explanation_for_anomaly(self, mine_name: str, metric: str, year: str) -> Optional[Dict[str, Any]]:
        queries = [
            f"{mine_name} {metric} {year} downtime expansion production reason delay increase decrease breakdown",
            f"{mine_name} production {year} operational issues geological condition expansion",
            f"{mine_name} {year}"
        ]
        
        for q in queries:
            matches = self.search(q, top_k=3)
            for m in matches:
                txt = m["text"].lower()
                # Check for explanatory keywords
                if any(w in txt for w in ["downtime", "expansion", "capacity", "disruption", "flooding", "strike", "equipment", "breakdown", "overburden", "increase", "adversely", "commissioned"]):
                    return m
        return None
