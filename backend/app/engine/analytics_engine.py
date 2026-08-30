from typing import List, Dict, Any, Optional
import math

class DeterministicAnalyticsEngine:
    @staticmethod
    def calculate_yoy_growth(current_val: float, previous_val: float) -> Optional[float]:
        if previous_val == 0:
            return None
        return round(((current_val - previous_val) / previous_val) * 100.0, 2)

    @staticmethod
    def calculate_cagr(start_val: float, end_val: float, num_years: int) -> Optional[float]:
        if start_val <= 0 or end_val <= 0 or num_years <= 0:
            return None
        return round(((end_val / start_val) ** (1.0 / num_years) - 1.0) * 100.0, 2)

    @staticmethod
    def aggregate_by_subsidiary(facts: List[Dict[str, Any]], metric: str = "Coal Production") -> Dict[str, Any]:
        filtered = [f for f in facts if f.get("metric") == metric and not f.get("is_superseded", False)]
        
        subsidiary_totals = {}
        year_set = set()
        
        for f in filtered:
            sub = f["subsidiary"]
            year = f["fiscal_year"]
            val = f["normalized_value"]
            year_set.add(year)
            
            if sub not in subsidiary_totals:
                subsidiary_totals[sub] = {}
            subsidiary_totals[sub][year] = round(subsidiary_totals[sub].get(year, 0.0) + val, 3)
            
        sorted_years = sorted(list(year_set))
        
        subsidiary_analytics = []
        for sub, yearly_vals in subsidiary_totals.items():
            first_year = sorted_years[0] if sorted_years else None
            last_year = sorted_years[-1] if sorted_years else None
            
            v_start = yearly_vals.get(first_year, 0.0)
            v_end = yearly_vals.get(last_year, 0.0)
            
            growth_pct = None
            if v_start > 0:
                growth_pct = round(((v_end - v_start) / v_start) * 100.0, 2)
                
            cagr_pct = None
            if len(sorted_years) > 1 and v_start > 0 and v_end > 0:
                cagr_pct = DeterministicAnalyticsEngine.calculate_cagr(v_start, v_end, len(sorted_years) - 1)
                
            subsidiary_analytics.append({
                "subsidiary": sub,
                "yearly_production": yearly_vals,
                "start_year_val": v_start,
                "end_year_val": v_end,
                "total_growth_pct": growth_pct,
                "cagr_pct": cagr_pct,
                "unit": "MT"
            })
            
        subsidiary_analytics.sort(key=lambda x: x["end_year_val"], reverse=True)
        
        return {
            "metric": metric,
            "years": sorted_years,
            "subsidiaries": subsidiary_analytics,
            "overall_total_start": sum(s["start_year_val"] for s in subsidiary_analytics),
            "overall_total_end": sum(s["end_year_val"] for s in subsidiary_analytics)
        }

    @staticmethod
    def aggregate_by_state(mines: List[Dict[str, Any]], facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        state_map = {m["code"]: m["state"] for m in mines}
        state_totals = {}
        
        for f in facts:
            if f.get("is_superseded"):
                continue
            m_code = f["mine_code"]
            state = state_map.get(m_code, "Other")
            val = f["normalized_value"]
            year = f["fiscal_year"]
            
            if state not in state_totals:
                state_totals[state] = {}
            state_totals[state][year] = round(state_totals[state].get(year, 0.0) + val, 2)
            
        results = []
        for state, yearly in state_totals.items():
            results.append({
                "state": state,
                "yearly_data": yearly,
                "latest_production": list(yearly.values())[-1] if yearly else 0.0
            })
        results.sort(key=lambda x: x["latest_production"], reverse=True)
        return results
