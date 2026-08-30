import pytest
from backend.app.engine.analytics_engine import DeterministicAnalyticsEngine

def test_yoy_growth_calculation():
    # 10 MT -> 12.5 MT = +25%
    growth = DeterministicAnalyticsEngine.calculate_yoy_growth(12.5, 10.0)
    assert growth == 25.0

    # 10 MT -> 5.0 MT = -50%
    drop = DeterministicAnalyticsEngine.calculate_yoy_growth(5.0, 10.0)
    assert drop == -50.0

def test_cagr_calculation():
    # 100 MT to 144 MT over 2 years = 20% CAGR (1.2^2 = 1.44)
    cagr = DeterministicAnalyticsEngine.calculate_cagr(100.0, 144.0, 2)
    assert cagr == 20.0

def test_subsidiary_aggregation():
    facts = [
        {"subsidiary": "BCCL", "fiscal_year": "2021-22", "normalized_value": 10.0, "metric": "Coal Production", "is_superseded": False},
        {"subsidiary": "BCCL", "fiscal_year": "2024-25", "normalized_value": 15.0, "metric": "Coal Production", "is_superseded": False},
        {"subsidiary": "SECL", "fiscal_year": "2021-22", "normalized_value": 50.0, "metric": "Coal Production", "is_superseded": False},
        {"subsidiary": "SECL", "fiscal_year": "2024-25", "normalized_value": 75.0, "metric": "Coal Production", "is_superseded": False}
    ]
    agg = DeterministicAnalyticsEngine.aggregate_by_subsidiary(facts)
    assert agg["overall_total_start"] == 60.0
    assert agg["overall_total_end"] == 90.0
    
    bccl = next(s for s in agg["subsidiaries"] if s["subsidiary"] == "BCCL")
    assert bccl["total_growth_pct"] == 50.0
