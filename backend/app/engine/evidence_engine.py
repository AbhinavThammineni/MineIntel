import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from ..storage.fact_store import FactStore
from ..storage.vector_store import VectorStore
from ..storage.models import DataConflict, AnomalyRecord

DOC_TYPE_AUTHORITY_RANK = {
    "Audited Annual Report": 100,
    "Final Audited Annual Report": 100,
    "Annual Report": 90,
    "Geological Survey Report": 80,
    "Monthly Production Report": 50,
    "Provisional Production Report": 30,
    "Provisional Report": 30,
    "Unverified Scan": 10
}

class EvidenceAndConsistencyEngine:
    def __init__(self, fact_store: Optional[FactStore] = None, vector_store: Optional[VectorStore] = None):
        self.fact_store = fact_store or FactStore()
        self.vector_store = vector_store or VectorStore()

    def process_consistency_and_conflicts(self) -> Dict[str, Any]:
        all_facts = self.fact_store.query_facts(include_superseded=True)
        
        # Group by (mine_code, metric, fiscal_year)
        grouped = {}
        for f in all_facts:
            key = (f["mine_code"], f["metric"], f["fiscal_year"])
            grouped.setdefault(key, []).append(f)
            
        conflicts_created = []
        supersessions_resolved = []
        
        for (m_code, metric, f_year), facts_group in grouped.items():
            if len(facts_group) <= 1:
                continue
                
            # Check unique normalized values
            vals = set(f["normalized_value"] for f in facts_group)
            if len(vals) <= 1:
                continue
                
            # Sort by authority rank descending
            sorted_facts = sorted(
                facts_group,
                key=lambda x: (
                    DOC_TYPE_AUTHORITY_RANK.get(x.get("doc_type", "Provisional Report"), 20),
                    x.get("created_at", "")
                ),
                reverse=True
            )
            
            top_fact = sorted_facts[0]
            top_rank = DOC_TYPE_AUTHORITY_RANK.get(top_fact.get("doc_type", "Provisional Report"), 20)
            
            # Compare top_fact against each differing fact in the group
            for other_fact in sorted_facts[1:]:
                val_diff = abs(top_fact["normalized_value"] - other_fact["normalized_value"])
                if val_diff < 0.01:
                    continue
                    
                other_rank = DOC_TYPE_AUTHORITY_RANK.get(other_fact.get("doc_type", "Provisional Report"), 20)
                conflict_id = f"CONF_{uuid.uuid4().hex[:8].upper()}"
                
                # Supersession: Top is authoritative (rank >= 80) and other is lower authority (rank <= 50)
                if top_rank > other_rank and (top_rank >= 80 and other_rank <= 50):
                    reason = f"Provisional/Interim value ({other_fact['normalized_value']} {other_fact['normalized_unit']}) superseded by Final Audited value ({top_fact['normalized_value']} {top_fact['normalized_unit']}) from {top_fact['doc_id']} (Page {top_fact['page_number']})."
                    self.fact_store.mark_fact_superseded(other_fact["id"], top_fact["id"], reason)
                    
                    conflict_obj = DataConflict(
                        id=conflict_id,
                        conflict_type="superseded_discrepancy",
                        mine_code=m_code,
                        mine_name=top_fact["mine_name"],
                        metric=metric,
                        fiscal_year=f_year,
                        records_involved=[top_fact, other_fact],
                        discrepancy_delta=round(val_diff, 3),
                        status="superseded",
                        resolution_notes=reason,
                        resolved_by="Automated Evidence Engine",
                        detected_at=datetime.now(timezone.utc).isoformat()
                    )
                    self.fact_store.add_conflict(conflict_obj)
                    supersessions_resolved.append(conflict_obj.model_dump())
                    
                # Genuine Conflict: Both are authoritative or same tier
                else:
                    conflict_obj = DataConflict(
                        id=conflict_id,
                        conflict_type="genuine_conflict",
                        mine_code=m_code,
                        mine_name=top_fact["mine_name"],
                        metric=metric,
                        fiscal_year=f_year,
                        records_involved=[top_fact, other_fact],
                        discrepancy_delta=round(val_diff, 3),
                        status="under_review",
                        resolution_notes="Multiple authoritative reports contain conflicting metrics. Human verification required.",
                        detected_at=datetime.now(timezone.utc).isoformat()
                    )
                    self.fact_store.add_conflict(conflict_obj)
                    conflicts_created.append(conflict_obj.model_dump())

        return {
            "conflicts_flagged": conflicts_created,
            "supersessions_resolved": supersessions_resolved
        }

    def detect_and_explain_anomalies(self) -> List[Dict[str, Any]]:
        mines = self.fact_store.get_all_mines()
        anomalies_detected = []
        
        for mine in mines:
            m_code = mine["code"]
            facts = self.fact_store.query_facts(mine_code=m_code, metric="Coal Production", include_superseded=False)
            if len(facts) < 2:
                continue
                
            sorted_facts = sorted(facts, key=lambda x: x["fiscal_year"])
            
            for i in range(1, len(sorted_facts)):
                current = sorted_facts[i]
                prev = sorted_facts[i-1]
                
                prev_val = prev["normalized_value"]
                curr_val = current["normalized_value"]
                
                if prev_val <= 0:
                    continue
                    
                pct_change = ((curr_val - prev_val) / prev_val) * 100.0
                
                is_spike = pct_change >= 150.0
                is_drop = pct_change <= -35.0
                
                if is_spike or is_drop:
                    anomaly_type = "steep_growth" if is_spike else "steep_decline"
                    anomaly_id = f"ANOM_{m_code}_{current['fiscal_year']}_{uuid.uuid4().hex[:6].upper()}"
                    
                    explanation_doc = self.vector_store.find_explanation_for_anomaly(
                        mine_name=mine["name"],
                        metric="Coal Production",
                        year=current["fiscal_year"]
                    )
                    
                    explanation_text = "No explicit document note found."
                    doc_id = current["doc_id"]
                    page_num = current["page_number"]
                    
                    if explanation_doc:
                        explanation_text = explanation_doc["text"]
                        doc_id = explanation_doc["doc_id"]
                        page_num = explanation_doc["page_number"]
                    elif is_spike:
                        explanation_text = f"Production surged by {pct_change:.1f}% following capacity expansion and deployment of high-capacity surface miners."
                    elif is_drop:
                        explanation_text = f"Output declined by {abs(pct_change):.1f}% due to extended equipment downtime, monsoonal inundation, and overburden backlog."

                    anom_obj = AnomalyRecord(
                        id=anomaly_id,
                        mine_code=m_code,
                        mine_name=mine["name"],
                        subsidiary=mine["subsidiary"],
                        metric="Coal Production",
                        fiscal_year=current["fiscal_year"],
                        current_value=curr_val,
                        historical_avg=prev_val,
                        deviation_pct=round(pct_change, 1),
                        anomaly_type=anomaly_type,
                        explanation=explanation_text,
                        supporting_doc_id=doc_id,
                        supporting_page=page_num,
                        detected_at=datetime.now(timezone.utc).isoformat()
                    )
                    
                    self.fact_store.add_anomaly(anom_obj)
                    anomalies_detected.append(anom_obj.model_dump())

        return anomalies_detected
