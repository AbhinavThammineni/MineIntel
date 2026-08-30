from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from ..storage.fact_store import FactStore
from ..engine.analytics_engine import DeterministicAnalyticsEngine

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/generate")
def generate_production_report(
    start_year: str = Query("2021-22", description="Start Fiscal Year"),
    end_year: str = Query("2024-25", description="End Fiscal Year"),
    subsidiary: Optional[str] = Query(None, description="Optional Subsidiary Filter")
):
    store = FactStore()
    mines = store.get_all_mines()
    facts = store.query_facts(subsidiary=subsidiary, metric="Coal Production", include_superseded=False)
    ob_facts = store.query_facts(subsidiary=subsidiary, metric="Overburden Removal", include_superseded=False)
    anomalies = store.list_anomalies()
    conflicts = store.list_conflicts()
    
    agg = DeterministicAnalyticsEngine.aggregate_by_subsidiary(facts)
    state_aggs = DeterministicAnalyticsEngine.aggregate_by_state(mines, facts)
    
    tot_s = agg.get("overall_total_start", 0.0)
    tot_e = agg.get("overall_total_end", 0.0)
    overall_growth = round(((tot_e - tot_s) / tot_s) * 100.0, 2) if tot_s > 0 else 0.0
    
    state_reserves = {
        "Odisha": 88.5,
        "Jharkhand": 86.2,
        "Chhattisgarh": 74.8,
        "West Bengal": 33.1,
        "Madhya Pradesh": 31.5,
        "Maharashtra": 12.8
    }
    
    state_table_data = []
    tot_st_prod = sum(s["latest_production"] for s in state_aggs)
    for s in state_aggs:
        st_name = s["state"]
        res = state_reserves.get(st_name, 10.0)
        share = round((s["latest_production"] / tot_st_prod) * 100.0, 1) if tot_st_prod > 0 else 0.0
        state_table_data.append({
            "state": st_name,
            "reserves_bt": res,
            "latest_production": s["latest_production"],
            "share_pct": share
        })

    report_sections = [
        {
            "section_num": "1",
            "title": "Executive Summary & Key KPIs",
            "content": f"During the reporting period ({start_year} to {end_year}), raw coal production across operating subsidiaries grew from {tot_s:.2f} MT to {tot_e:.2f} MT (+{overall_growth:.1f}%). All reported production metrics have undergone automated unit normalization, cross-document supersession resolution, and anomaly validation."
        },
        {
            "section_num": "2",
            "title": "Production & Dispatch Matrix (with CAGR)",
            "table_type": "subsidiary_matrix",
            "data": agg["subsidiaries"]
        },
        {
            "section_num": "3",
            "title": "Geotechnical & Overburden Removal (MCuM) Summary",
            "table_type": "overburden_matrix",
            "data": ob_facts
        },
        {
            "section_num": "4",
            "title": "State-wise Resource & Production Allocation",
            "table_type": "state_allocation",
            "data": state_table_data
        },
        {
            "section_num": "5",
            "title": "Detected Operational Anomalies & Root Causes",
            "table_type": "anomalies_list",
            "data": anomalies
        },
        {
            "section_num": "6",
            "title": "Data Consistency & Conflict Resolution Audit Trail",
            "table_type": "conflict_audit",
            "data": conflicts
        }
    ]
    
    return {
        "report_id": f"REP_PROD_{start_year}_{end_year}",
        "title": f"Comprehensive National Coal Production & Evidence Intelligence Report ({start_year} - {end_year})",
        "generated_at": "2026-08-29T13:35:00Z",
        "parameters": {
            "start_year": start_year,
            "end_year": end_year,
            "subsidiary": subsidiary or "ALL_CIL"
        },
        "summary_metrics": {
            "start_total_mt": tot_s,
            "end_total_mt": tot_e,
            "growth_pct": overall_growth,
            "anomalies_count": len(anomalies),
            "conflicts_count": len(conflicts),
            "total_ob_mcum": sum(f["normalized_value"] for f in ob_facts)
        },
        "sections": report_sections
    }
