import pytest
from backend.app.pipeline.normalizer import Normalizer
from backend.app.pipeline.ai_extractor import AIExtractionLayer

def test_unit_normalization():
    # 1. 12,500 KT -> 12.5 MT
    val, unit = Normalizer.normalize_unit("Coal Production", 12500.0, "KT")
    assert val == 12.5
    assert unit == "MT"

    # 2. 12,500,000 tonnes -> 12.5 MT
    val, unit = Normalizer.normalize_unit("Coal Production", 12500000.0, "tonnes")
    assert val == 12.5
    assert unit == "MT"

    # 3. 12.5 MT -> 12.5 MT
    val, unit = Normalizer.normalize_unit("Coal Production", 12.5, "MT")
    assert val == 12.5
    assert unit == "MT"

def test_alias_normalization():
    assert Normalizer.normalize_subsidiary("BCCL") == "BCCL"
    assert Normalizer.normalize_subsidiary("Bharat Coking Coal Limited") == "BCCL"
    assert Normalizer.normalize_subsidiary("Bharat Coking Coal Ltd.") == "BCCL"
    assert Normalizer.normalize_subsidiary("central coalfields limited") == "CCL"
    assert Normalizer.normalize_subsidiary("Coal India Limited") == "CIL"

def test_entity_resolution_and_ocr_healing():
    # Exact Match
    mine1 = Normalizer.resolve_mine_entity("Moonidih Underground Mine")
    assert mine1["code"] == "MINE_MOONIDIH"
    assert mine1["subsidiary"] == "BCCL"

    # OCR Typo Healing: "Moonidih" spelled "Moneedih"
    mine2 = Normalizer.resolve_mine_entity("Moneedih Underground", preferred_subsidiary="BCCL")
    assert mine2["code"] == "MINE_MOONIDIH"

    # Mine A
    mine3 = Normalizer.resolve_mine_entity("Mine A")
    assert mine3["code"] == "MINE_A"

def test_ai_fact_extraction():
    extractor = AIExtractionLayer()
    text = "Mine A produced 12.5 MT of coal during 2023."
    facts = extractor.extract_structured_facts_from_text(text, doc_id="DOC001", doc_type="Audited Annual Report", page_number=17)
    
    assert len(facts) == 1
    fact = facts[0]
    assert fact["mine_code"] == "MINE_A"
    assert fact["metric"] == "Coal Production"
    assert fact["normalized_value"] == 12.5
    assert fact["normalized_unit"] == "MT"
    assert fact["fiscal_year"] == "2023-24"
    assert fact["page_number"] == 17
    assert fact["bbox"]["x0"] == 72.0
