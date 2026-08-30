import pytest
from backend.app.storage.fact_store import FactStore
from backend.app.storage.vector_store import VectorStore
from backend.app.engine.evidence_engine import EvidenceAndConsistencyEngine
from backend.app.storage.models import FactRecord, MineEntity

def test_supersession_logic(tmp_path):
    db_file = tmp_path / "test_facts.db"
    store = FactStore(db_path=db_file)
    vector = VectorStore(storage_path=tmp_path / "test_vec.json")
    
    # 1. Insert Provisional Fact (10.2 MT)
    f_prov = FactRecord(
        id="FACT_PROV",
        doc_id="DOC_PROVISIONAL",
        doc_type="Provisional Production Report",
        page_number=4,
        mine_code="MINE_A",
        mine_name="Mine A Project",
        subsidiary="BCCL",
        metric="Coal Production",
        raw_value=10.2,
        raw_unit="MT",
        normalized_value=10.2,
        normalized_unit="MT",
        fiscal_year="2023-24"
    )
    store.add_fact(f_prov)

    # 2. Insert Audited Fact (12.5 MT)
    f_audit = FactRecord(
        id="FACT_AUDIT",
        doc_id="DOC_AUDITED",
        doc_type="Final Audited Annual Report",
        page_number=17,
        mine_code="MINE_A",
        mine_name="Mine A Project",
        subsidiary="BCCL",
        metric="Coal Production",
        raw_value=12.5,
        raw_unit="MT",
        normalized_value=12.5,
        normalized_unit="MT",
        fiscal_year="2023-24"
    )
    store.add_fact(f_audit)

    # 3. Run Evidence Engine
    engine = EvidenceAndConsistencyEngine(store, vector)
    result = engine.process_consistency_and_conflicts()

    assert len(result["supersessions_resolved"]) == 1
    sup = result["supersessions_resolved"][0]
    assert sup["mine_code"] == "MINE_A"
    assert sup["status"] == "superseded"
    assert "superseded" in sup["resolution_notes"].lower()

    # Query active facts (should only return the 12.5 MT audited fact)
    active_facts = store.query_facts(mine_code="MINE_A", fiscal_year="2023-24", include_superseded=False)
    assert len(active_facts) == 1
    assert active_facts[0]["normalized_value"] == 12.5

def test_genuine_conflict_detection(tmp_path):
    db_file = tmp_path / "test_facts_conf.db"
    store = FactStore(db_path=db_file)
    vector = VectorStore(storage_path=tmp_path / "test_vec.json")

    # Two authoritative reports disagreeing (1.85 MT vs 1.40 MT)
    f1 = FactRecord(
        id="FACT_1", doc_id="DOC_A", doc_type="Final Audited Annual Report", page_number=1,
        mine_code="MINE_MOONIDIH", mine_name="Moonidih Underground Mine", subsidiary="BCCL",
        metric="Coal Production", raw_value=1.85, raw_unit="MT", normalized_value=1.85, normalized_unit="MT", fiscal_year="2023-24"
    )
    f2 = FactRecord(
        id="FACT_2", doc_id="DOC_B", doc_type="Audited Annual Report", page_number=1,
        mine_code="MINE_MOONIDIH", mine_name="Moonidih Underground Mine", subsidiary="BCCL",
        metric="Coal Production", raw_value=1.40, raw_unit="MT", normalized_value=1.40, normalized_unit="MT", fiscal_year="2023-24"
    )
    store.add_fact(f1)
    store.add_fact(f2)

    engine = EvidenceAndConsistencyEngine(store, vector)
    result = engine.process_consistency_and_conflicts()

    assert len(result["conflicts_flagged"]) == 1
    conf = result["conflicts_flagged"][0]
    assert conf["conflict_type"] == "genuine_conflict"
    assert conf["status"] == "under_review"
    assert conf["discrepancy_delta"] == 0.45
