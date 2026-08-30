from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from ..storage.fact_store import FactStore
from ..engine.analytics_engine import DeterministicAnalyticsEngine

router = APIRouter(prefix="/api/gis", tags=["GIS"])

@router.get("/mines")
def get_gis_mines():
    store = FactStore()
    mines = store.get_all_mines()
    facts = store.query_facts(metric="Coal Production", include_superseded=False)
    anomalies = store.list_anomalies()
    conflicts = store.list_conflicts(status="under_review")
    
    facts_by_mine = {}
    for f in facts:
        facts_by_mine.setdefault(f["mine_code"], []).append(f)
        
    anom_mine_codes = {a["mine_code"]: a for a in anomalies}
    conf_mine_codes = {c["mine_code"]: c for c in conflicts}
    
    result = []
    for m in mines:
        m_code = m["code"]
        m_facts = sorted(facts_by_mine.get(m_code, []), key=lambda x: x["fiscal_year"])
        
        yearly_prod = {f["fiscal_year"]: f["normalized_value"] for f in m_facts}
        latest_val = m_facts[-1]["normalized_value"] if m_facts else 0.0
        latest_year = m_facts[-1]["fiscal_year"] if m_facts else "N/A"
        
        has_anom = m_code in anom_mine_codes
        has_conf = m_code in conf_mine_codes
        
        status_color = "green"
        if has_conf:
            status_color = "red"
        elif has_anom:
            status_color = "orange"
            
        result.append({
            "id": m["id"],
            "code": m_code,
            "name": m["name"],
            "subsidiary": m["subsidiary"],
            "state": m["state"],
            "district": m["district"],
            "latitude": m["lat"],
            "longitude": m["lng"],
            "lat": m["lat"],
            "lng": m["lng"],
            "mine_type": m["mine_type"],
            "operational_status": m["operational_status"],
            "latest_production": latest_val,
            "latest_fiscal_year": latest_year,
            "unit": "MT",
            "yearly_production": yearly_prod,
            "has_anomaly": has_anom,
            "anomaly_detail": anom_mine_codes.get(m_code),
            "has_conflict": has_conf,
            "conflict_detail": conf_mine_codes.get(m_code),
            "status_color": status_color
        })
        
    return result

@router.get("/mine/{mine_code}")
def get_mine_details(mine_code: str):
    store = FactStore()
    mines = store.get_all_mines()
    mine = next((m for m in mines if m["code"] == mine_code), None)
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
        
    facts = store.query_facts(mine_code=mine_code, metric="Coal Production", include_superseded=False)
    ob_facts = store.query_facts(mine_code=mine_code, metric="Overburden Removal", include_superseded=False)
    anomalies = [a for a in store.list_anomalies() if a["mine_code"] == mine_code]
    conflicts = [c for c in store.list_conflicts() if c["mine_code"] == mine_code]
    
    return {
        "mine": {
            "id": mine["id"],
            "code": mine["code"],
            "name": mine["name"],
            "subsidiary": mine["subsidiary"],
            "state": mine["state"],
            "district": mine["district"],
            "latitude": mine["lat"],
            "longitude": mine["lng"],
            "mine_type": mine["mine_type"],
            "operational_status": mine["operational_status"]
        },
        "facts": sorted(facts, key=lambda x: x["fiscal_year"]),
        "overburden_facts": sorted(ob_facts, key=lambda x: x["fiscal_year"]),
        "anomalies": anomalies,
        "conflicts": conflicts
    }

@router.get("/state_aggregates")
def get_state_aggregates():
    store = FactStore()
    mines = store.get_all_mines()
    facts = store.query_facts(metric="Coal Production", include_superseded=False)
    return DeterministicAnalyticsEngine.aggregate_by_state(mines, facts)
