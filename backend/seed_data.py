import os
import sys
from pathlib import Path

# UTF-8 stdout
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')


# Add app to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.storage.models import MineEntity, DocumentMetadata, FactRecord
from app.storage.fact_store import FactStore
from app.storage.vector_store import VectorStore
from app.storage.graph_store import MiningGraphStore
from app.engine.evidence_engine import EvidenceAndConsistencyEngine

def seed_all():
    print("🌱 Initializing MineIntel Tri-Store & Seeding Core Mining Intelligence...")
    fact_store = FactStore()
    vector_store = VectorStore()
    graph_store = MiningGraphStore()
    
    # 1. Master Mines
    mines = [
        # BCCL Mines (Jharkhand)
        MineEntity(id="M01", code="MINE_A", name="Mine A Project", normalized_name="Mine A Project", subsidiary="BCCL", state="Jharkhand", district="Dhanbad", lat=23.7957, lng=86.4304, mine_type="Opencast"),
        MineEntity(id="M02", code="MINE_B", name="Mine B Project", normalized_name="Mine B Project", subsidiary="BCCL", state="Jharkhand", district="Dhanbad", lat=23.7800, lng=86.3800, mine_type="Opencast"),
        MineEntity(id="M03", code="MINE_MOONIDIH", name="Moonidih Underground Mine", normalized_name="Moonidih Underground Mine", subsidiary="BCCL", state="Jharkhand", district="Dhanbad", lat=23.7410, lng=86.3520, mine_type="Underground"),
        MineEntity(id="M04", code="MINE_BLOCK2", name="Block II Opencast Mine", normalized_name="Block II Opencast Mine", subsidiary="BCCL", state="Jharkhand", district="Dhanbad", lat=23.8120, lng=86.2150, mine_type="Opencast"),
        MineEntity(id="M05", code="MINE_KUSUNDA", name="Kusunda Opencast Mine", normalized_name="Kusunda Opencast Mine", subsidiary="BCCL", state="Jharkhand", district="Dhanbad", lat=23.7780, lng=86.4120, mine_type="Opencast"),
        
        # SECL Mines (Chhattisgarh)
        MineEntity(id="M06", code="MINE_GEVRA", name="Gevra Opencast Project", normalized_name="Gevra Opencast Project", subsidiary="SECL", state="Chhattisgarh", district="Korba", lat=22.3480, lng=82.5930, mine_type="Opencast"),
        MineEntity(id="M07", code="MINE_KUSMUNDA", name="Kusmunda Opencast Mine", normalized_name="Kusmunda Opencast Mine", subsidiary="SECL", state="Chhattisgarh", district="Korba", lat=22.3210, lng=82.6820, mine_type="Opencast"),
        MineEntity(id="M08", code="MINE_DIPKA", name="Dipka Opencast Project", normalized_name="Dipka Opencast Project", subsidiary="SECL", state="Chhattisgarh", district="Korba", lat=22.3150, lng=82.5510, mine_type="Opencast"),
        
        # MCL Mines (Odisha)
        MineEntity(id="M09", code="MINE_BHUBANESWARI", name="Bhubaneswari Opencast Mine", normalized_name="Bhubaneswari Opencast Mine", subsidiary="MCL", state="Odisha", district="Angul", lat=20.9520, lng=85.1230, mine_type="Opencast"),
        MineEntity(id="M10", code="MINE_LAKHANPUR", name="Lakhanpur Opencast Project", normalized_name="Lakhanpur Opencast Project", subsidiary="MCL", state="Odisha", district="Jharsuguda", lat=21.7580, lng=83.8210, mine_type="Opencast"),
        
        # CCL Mines (Jharkhand)
        MineEntity(id="M11", code="MINE_PIPARWAR", name="Piparwar Opencast Mine", normalized_name="Piparwar Opencast Mine", subsidiary="CCL", state="Jharkhand", district="Chatra", lat=23.7120, lng=85.0340, mine_type="Opencast"),
        MineEntity(id="M12", code="MINE_ASHOKA", name="Ashoka Opencast Project", normalized_name="Ashoka Opencast Project", subsidiary="CCL", state="Jharkhand", district="Chatra", lat=23.7380, lng=85.0510, mine_type="Opencast"),
        MineEntity(id="M13", code="MINE_AMRAPALI", name="Amrapali Opencast Mine", normalized_name="Amrapali Opencast Mine", subsidiary="CCL", state="Jharkhand", district="Chatra", lat=23.8210, lng=84.9820, mine_type="Opencast"),
        
        # ECL Mines (West Bengal / Jharkhand)
        MineEntity(id="M14", code="MINE_RAJMAHAL", name="Rajmahal Opencast Project", normalized_name="Rajmahal Opencast Project", subsidiary="ECL", state="Jharkhand", district="Godda", lat=25.0420, lng=87.3810, mine_type="Opencast"),
        MineEntity(id="M15", code="MINE_SONEPUR", name="Sonepur Bazari Project", normalized_name="Sonepur Bazari Project", subsidiary="ECL", state="West Bengal", district="Paschim Bardhaman", lat=23.6820, lng=87.2140, mine_type="Opencast"),
        
        # NCL Mines (Madhya Pradesh)
        MineEntity(id="M16", code="MINE_JAYANT", name="Jayant Opencast Project", normalized_name="Jayant Opencast Project", subsidiary="NCL", state="Madhya Pradesh", district="Singrauli", lat=24.1120, lng=82.6450, mine_type="Opencast"),
        MineEntity(id="M17", code="MINE_NIGAHI", name="Nigahi Opencast Mine", normalized_name="Nigahi Opencast Mine", subsidiary="NCL", state="Madhya Pradesh", district="Singrauli", lat=24.1350, lng=82.6020, mine_type="Opencast"),
        
        # WCL Mines (Maharashtra)
        MineEntity(id="M18", code="MINE_UMRER", name="Umrer Opencast Mine", normalized_name="Umrer Opencast Mine", subsidiary="WCL", state="Maharashtra", district="Nagpur", lat=20.8520, lng=79.3240, mine_type="Opencast"),
        MineEntity(id="M19", code="MINE_PENGANGA", name="Penganga Opencast Project", normalized_name="Penganga Opencast Project", subsidiary="WCL", state="Maharashtra", district="Chandrapur", lat=19.9820, lng=79.2810, mine_type="Opencast")
    ]
    
    for m in mines:
        fact_store.add_mine(m)
    print(f"✓ Added {len(mines)} Master Mines across 7 CIL subsidiaries.")
    
    # 2. Documents Metadata
    docs = [
        DocumentMetadata(id="DOC001_ANNUAL_REPORT_2024", filename="Annual_Report_2024.pdf", file_type="pdf", title="Coal India Limited Audited Annual Report 2023-24", doc_type="Final Audited Annual Report", reporting_period="2023-24", page_count=180, source_author="CIL Statutory Audit Committee"),
        DocumentMetadata(id="DOC002_PROVISIONAL_REPORT_2023", filename="Provisional_Production_Record.pdf", file_type="pdf", title="Provisional Monthly Production Flash Report 2023", doc_type="Provisional Production Report", reporting_period="2023-24", page_count=12, source_author="Field Operations Directorate"),
        DocumentMetadata(id="DOC003_MONTHLY_DISPATCH_EXCEL", filename="Production_Data_2023.xlsx", file_type="xlsx", title="CIL Consolidated Subsidiary Dispatch Matrix", doc_type="Monthly Production Report", reporting_period="2023-24", page_count=1, source_author="Marketing & Sales Division"),
        DocumentMetadata(id="DOC004_GEOLOGICAL_REPORT_2024", filename="Geological_Operational_Review.docx", file_type="docx", title="Operational Variations & Equipment Reliability Review", doc_type="Geological Survey Report", reporting_period="2020-2025", page_count=45, source_author="CMPDI Operational Audit"),
        DocumentMetadata(id="DOC005_STATUTORY_DISCLOSURE", filename="Statutory_Annual_Report_B.pdf", file_type="pdf", title="Subsidiary Annual Disclosure Report 2024", doc_type="Audited Annual Report", reporting_period="2023-24", page_count=95, source_author="BCCL External Auditor")
    ]
    
    for d in docs:
        fact_store.add_document(d)
    print(f"✓ Registered {len(docs)} Authority Documents.")
    
    # 3. Facts with Provenance and Bounding Boxes
    facts = [
        # Multi-year trajectory for Mine A (Illustrates Historical Stability + 2023 Corroboration + 2024 Anomaly Spike)
        FactRecord(id="F_MA_2020", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=14, bbox={"x0": 72, "y0": 140, "x1": 480, "y1": 165}, raw_text="Mine A produced 10.0 MT of coal during 2020.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=10.0, raw_unit="MT", normalized_value=10.0, normalized_unit="MT", fiscal_year="2020-21"),
        FactRecord(id="F_MA_2021", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=15, bbox={"x0": 72, "y0": 180, "x1": 480, "y1": 205}, raw_text="Mine A produced 11.0 MT of coal during 2021.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=11.0, raw_unit="MT", normalized_value=11.0, normalized_unit="MT", fiscal_year="2021-22"),
        FactRecord(id="F_MA_2022", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=16, bbox={"x0": 72, "y0": 210, "x1": 480, "y1": 235}, raw_text="Mine A produced 10.5 MT of coal during 2022.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=10.5, raw_unit="MT", normalized_value=10.5, normalized_unit="MT", fiscal_year="2022-23"),
        
        # 2023 Facts: Report A (12.5 MT), Report B (12,500 KT -> 12.5 MT), Report C Provisional (10.2 MT -> will be superseded)
        FactRecord(id="F_MA_2023_AUDITED", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=17, bbox={"x0": 72, "y0": 250, "x1": 510, "y1": 278}, raw_text="Mine A produced 12.5 MT of coal during 2023.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=12.5, raw_unit="MT", normalized_value=12.5, normalized_unit="MT", fiscal_year="2023-24"),
        FactRecord(id="F_MA_2023_EXCEL", doc_id="DOC003_MONTHLY_DISPATCH_EXCEL", doc_type="Monthly Production Report", page_number=1, bbox={"x0": 80, "y0": 110, "x1": 420, "y1": 135}, raw_text="Mine A dispatch record: 12,500 KT during 2023", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=12500.0, raw_unit="KT", normalized_value=12.5, normalized_unit="MT", fiscal_year="2023-24"),
        FactRecord(id="F_MA_2023_PROV", doc_id="DOC002_PROVISIONAL_REPORT_2023", doc_type="Provisional Production Report", page_number=4, bbox={"x0": 65, "y0": 190, "x1": 450, "y1": 215}, raw_text="Mine A provisional output: 10.2 MT in 2023", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=10.2, raw_unit="MT", normalized_value=10.2, normalized_unit="MT", fiscal_year="2023-24"),
        
        # 2024 Fact: 40 MT Anomaly Spike!
        FactRecord(id="F_MA_2024_ANOM", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=18, bbox={"x0": 72, "y0": 290, "x1": 520, "y1": 318}, raw_text="Mine A produced 40.0 MT of coal during 2024 following major pit expansion.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Coal Production", raw_value=40.0, raw_unit="MT", normalized_value=40.0, normalized_unit="MT", fiscal_year="2024-25"),
        
        # Mine B Project
        FactRecord(id="F_MB_2022", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=22, bbox={"x0": 72, "y0": 130, "x1": 480, "y1": 155}, raw_text="Mine B produced 8.0 MT in 2022.", mine_code="MINE_B", mine_name="Mine B Project", subsidiary="BCCL", metric="Coal Production", raw_value=8.0, raw_unit="MT", normalized_value=8.0, normalized_unit="MT", fiscal_year="2022-23"),
        FactRecord(id="F_MB_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=22, bbox={"x0": 72, "y0": 160, "x1": 480, "y1": 185}, raw_text="Mine B produced 9.0 MT in 2023.", mine_code="MINE_B", mine_name="Mine B Project", subsidiary="BCCL", metric="Coal Production", raw_value=9.0, raw_unit="MT", normalized_value=9.0, normalized_unit="MT", fiscal_year="2023-24"),
        FactRecord(id="F_MB_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=23, bbox={"x0": 72, "y0": 190, "x1": 480, "y1": 215}, raw_text="Mine B produced 11.0 MT in 2024.", mine_code="MINE_B", mine_name="Mine B Project", subsidiary="BCCL", metric="Coal Production", raw_value=11.0, raw_unit="MT", normalized_value=11.0, normalized_unit="MT", fiscal_year="2024-25"),
        
        # Gevra Mega Project (SECL)
        FactRecord(id="F_GEV_2021", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=45, bbox={"x0": 70, "y0": 120, "x1": 500, "y1": 145}, raw_text="Gevra produced 49.0 MT in 2021.", mine_code="MINE_GEVRA", mine_name="Gevra Opencast Project", subsidiary="SECL", metric="Coal Production", raw_value=49.0, raw_unit="MT", normalized_value=49.0, normalized_unit="MT", fiscal_year="2021-22"),
        FactRecord(id="F_GEV_2022", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=45, bbox={"x0": 70, "y0": 150, "x1": 500, "y1": 175}, raw_text="Gevra produced 52.5 MT in 2022.", mine_code="MINE_GEVRA", mine_name="Gevra Opencast Project", subsidiary="SECL", metric="Coal Production", raw_value=52.5, raw_unit="MT", normalized_value=52.5, normalized_unit="MT", fiscal_year="2022-23"),
        FactRecord(id="F_GEV_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=46, bbox={"x0": 70, "y0": 180, "x1": 500, "y1": 205}, raw_text="Gevra produced 59.0 MT in 2023.", mine_code="MINE_GEVRA", mine_name="Gevra Opencast Project", subsidiary="SECL", metric="Coal Production", raw_value=59.0, raw_unit="MT", normalized_value=59.0, normalized_unit="MT", fiscal_year="2023-24"),
        FactRecord(id="F_GEV_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=47, bbox={"x0": 70, "y0": 210, "x1": 500, "y1": 235}, raw_text="Gevra achieved historic record production of 70.0 MT in 2024.", mine_code="MINE_GEVRA", mine_name="Gevra Opencast Project", subsidiary="SECL", metric="Coal Production", raw_value=70.0, raw_unit="MT", normalized_value=70.0, normalized_unit="MT", fiscal_year="2024-25"),
        
        # Kusmunda (SECL)
        FactRecord(id="F_KUS_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=50, bbox={"x0": 70, "y0": 150, "x1": 490, "y1": 175}, raw_text="Kusmunda recorded 43.0 MT in 2023.", mine_code="MINE_KUSMUNDA", mine_name="Kusmunda Opencast Mine", subsidiary="SECL", metric="Coal Production", raw_value=43.0, raw_unit="MT", normalized_value=43.0, normalized_unit="MT", fiscal_year="2023-24"),
        FactRecord(id="F_KUS_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=51, bbox={"x0": 70, "y0": 180, "x1": 490, "y1": 205}, raw_text="Kusmunda recorded 50.0 MT in 2024.", mine_code="MINE_KUSMUNDA", mine_name="Kusmunda Opencast Mine", subsidiary="SECL", metric="Coal Production", raw_value=50.0, raw_unit="MT", normalized_value=50.0, normalized_unit="MT", fiscal_year="2024-25"),
        
        # Bhubaneswari (MCL)
        FactRecord(id="F_BHU_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=62, bbox={"x0": 75, "y0": 140, "x1": 510, "y1": 165}, raw_text="Bhubaneswari produced 31.0 MT in 2023.", mine_code="MINE_BHUBANESWARI", mine_name="Bhubaneswari Opencast Mine", subsidiary="MCL", metric="Coal Production", raw_value=31.0, raw_unit="MT", normalized_value=31.0, normalized_unit="MT", fiscal_year="2023-24"),
        FactRecord(id="F_BHU_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=63, bbox={"x0": 75, "y0": 170, "x1": 510, "y1": 195}, raw_text="Bhubaneswari produced 35.5 MT in 2024.", mine_code="MINE_BHUBANESWARI", mine_name="Bhubaneswari Opencast Mine", subsidiary="MCL", metric="Coal Production", raw_value=35.5, raw_unit="MT", normalized_value=35.5, normalized_unit="MT", fiscal_year="2024-25"),
        
        # Rajmahal (ECL) - Demonstrates steep decline anomaly due to pit flooding
        FactRecord(id="F_RAJ_2022", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=78, bbox={"x0": 72, "y0": 140, "x1": 500, "y1": 165}, raw_text="Rajmahal produced 17.0 MT in 2022.", mine_code="MINE_RAJMAHAL", mine_name="Rajmahal Opencast Project", subsidiary="ECL", metric="Coal Production", raw_value=17.0, raw_unit="MT", normalized_value=17.0, normalized_unit="MT", fiscal_year="2022-23"),
        FactRecord(id="F_RAJ_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=79, bbox={"x0": 72, "y0": 170, "x1": 500, "y1": 195}, raw_text="Rajmahal produced 9.5 MT in 2023.", mine_code="MINE_RAJMAHAL", mine_name="Rajmahal Opencast Project", subsidiary="ECL", metric="Coal Production", raw_value=9.5, raw_unit="MT", normalized_value=9.5, normalized_unit="MT", fiscal_year="2023-24"),
        
        # Genuine Conflict Fact on Moonidih (DOC001 vs DOC005)
        FactRecord(id="F_MOON_2023_A", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=35, bbox={"x0": 72, "y0": 120, "x1": 490, "y1": 145}, raw_text="Moonidih Underground Mine produced 1.85 MT of coking coal in 2023.", mine_code="MINE_MOONIDIH", mine_name="Moonidih Underground Mine", subsidiary="BCCL", metric="Coal Production", raw_value=1.85, raw_unit="MT", normalized_value=1.85, normalized_unit="MT", fiscal_year="2023-24"),
        
        # Overburden Removal Facts (in MCuM)
        FactRecord(id="F_OB_GEV_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=48, bbox={"x0": 70, "y0": 130, "x1": 510, "y1": 155}, raw_text="Gevra opencast overburden removal stood at 78.5 MCuM in 2023-24.", mine_code="MINE_GEVRA", mine_name="Gevra Opencast Project", subsidiary="SECL", metric="Overburden Removal", raw_value=78.5, raw_unit="MCuM", normalized_value=78.5, normalized_unit="MCuM", fiscal_year="2023-24"),
        FactRecord(id="F_OB_GEV_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=49, bbox={"x0": 70, "y0": 160, "x1": 510, "y1": 185}, raw_text="Gevra opencast overburden removal reached 92.0 MCuM in 2024-25.", mine_code="MINE_GEVRA", mine_name="Gevra Opencast Project", subsidiary="SECL", metric="Overburden Removal", raw_value=92.0, raw_unit="MCuM", normalized_value=92.0, normalized_unit="MCuM", fiscal_year="2024-25"),
        FactRecord(id="F_OB_KUS_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=52, bbox={"x0": 70, "y0": 140, "x1": 510, "y1": 165}, raw_text="Kusmunda overburden removal recorded at 54.0 MCuM in 2023-24.", mine_code="MINE_KUSMUNDA", mine_name="Kusmunda Opencast Mine", subsidiary="SECL", metric="Overburden Removal", raw_value=54.0, raw_unit="MCuM", normalized_value=54.0, normalized_unit="MCuM", fiscal_year="2023-24"),
        FactRecord(id="F_OB_KUS_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=53, bbox={"x0": 70, "y0": 170, "x1": 510, "y1": 195}, raw_text="Kusmunda overburden removal recorded at 65.0 MCuM in 2024-25.", mine_code="MINE_KUSMUNDA", mine_name="Kusmunda Opencast Mine", subsidiary="SECL", metric="Overburden Removal", raw_value=65.0, raw_unit="MCuM", normalized_value=65.0, normalized_unit="MCuM", fiscal_year="2024-25"),
        FactRecord(id="F_OB_MA_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=19, bbox={"x0": 72, "y0": 140, "x1": 500, "y1": 165}, raw_text="Mine A overburden removal was 22.0 MCuM in 2023-24.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Overburden Removal", raw_value=22.0, raw_unit="MCuM", normalized_value=22.0, normalized_unit="MCuM", fiscal_year="2023-24"),
        FactRecord(id="F_OB_MA_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=20, bbox={"x0": 72, "y0": 170, "x1": 500, "y1": 195}, raw_text="Mine A overburden removal increased to 68.0 MCuM in 2024-25 during pit expansion.", mine_code="MINE_A", mine_name="Mine A Project", subsidiary="BCCL", metric="Overburden Removal", raw_value=68.0, raw_unit="MCuM", normalized_value=68.0, normalized_unit="MCuM", fiscal_year="2024-25"),
        FactRecord(id="F_OB_BHU_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=64, bbox={"x0": 75, "y0": 130, "x1": 500, "y1": 155}, raw_text="Bhubaneswari overburden removal stood at 38.0 MCuM in 2023-24.", mine_code="MINE_BHUBANESWARI", mine_name="Bhubaneswari Opencast Mine", subsidiary="MCL", metric="Overburden Removal", raw_value=38.0, raw_unit="MCuM", normalized_value=38.0, normalized_unit="MCuM", fiscal_year="2023-24"),
        FactRecord(id="F_OB_BHU_2024", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=65, bbox={"x0": 75, "y0": 160, "x1": 500, "y1": 185}, raw_text="Bhubaneswari overburden removal reached 44.0 MCuM in 2024-25.", mine_code="MINE_BHUBANESWARI", mine_name="Bhubaneswari Opencast Mine", subsidiary="MCL", metric="Overburden Removal", raw_value=44.0, raw_unit="MCuM", normalized_value=44.0, normalized_unit="MCuM", fiscal_year="2024-25"),
        FactRecord(id="F_OB_RAJ_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=80, bbox={"x0": 72, "y0": 140, "x1": 500, "y1": 165}, raw_text="Rajmahal overburden removal was restricted to 11.5 MCuM in 2023-24 due to bench slip.", mine_code="MINE_RAJMAHAL", mine_name="Rajmahal Opencast Project", subsidiary="ECL", metric="Overburden Removal", raw_value=11.5, raw_unit="MCuM", normalized_value=11.5, normalized_unit="MCuM", fiscal_year="2023-24"),
        FactRecord(id="F_OB_JAY_2023", doc_id="DOC001_ANNUAL_REPORT_2024", doc_type="Final Audited Annual Report", page_number=88, bbox={"x0": 70, "y0": 140, "x1": 500, "y1": 165}, raw_text="Jayant overburden removal stood at 45.0 MCuM in 2023-24.", mine_code="MINE_JAYANT", mine_name="Jayant Opencast Project", subsidiary="NCL", metric="Overburden Removal", raw_value=45.0, raw_unit="MCuM", normalized_value=45.0, normalized_unit="MCuM", fiscal_year="2023-24"),
        FactRecord(id="F_MOON_2023_B", doc_id="DOC005_STATUTORY_DISCLOSURE", doc_type="Audited Annual Report", page_number=12, bbox={"x0": 80, "y0": 210, "x1": 500, "y1": 235}, raw_text="Moonidih Underground Mine produced 1.40 MT of coking coal in 2023.", mine_code="MINE_MOONIDIH", mine_name="Moonidih Underground Mine", subsidiary="BCCL", metric="Coal Production", raw_value=1.40, raw_unit="MT", normalized_value=1.40, normalized_unit="MT", fiscal_year="2023-24")
    ]
    
    for f in facts:
        fact_store.add_fact(f)
    print(f"✓ Inserted {len(facts)} Fact Records.")
    
    # 4. Semantic Text Chunks for Vector Store
    vector_store.add_chunk(
        doc_id="DOC001_ANNUAL_REPORT_2024",
        page_number=17,
        text="Mine A produced 12.5 MT of coal during 2023. Operational parameters stabilized with consistent coal beneficiation throughput.",
        bbox={"x0": 72, "y0": 250, "x1": 510, "y1": 278},
        section="BCCL Production Review"
    )
    vector_store.add_chunk(
        doc_id="DOC001_ANNUAL_REPORT_2024",
        page_number=18,
        text="Production capacity increased sharply after Mine A expansion project was commissioned with 4 new continuous surface miners in 2024, reaching 40 MT output.",
        bbox={"x0": 72, "y0": 290, "x1": 520, "y1": 318},
        section="BCCL Strategic Expansion"
    )
    vector_store.add_chunk(
        doc_id="DOC004_GEOLOGICAL_REPORT_2024",
        page_number=15,
        text="Why did BCCL production decrease in 2023? Production was adversely affected by prolonged equipment downtime, heavy monsoonal pit inundation, and geological faulting in Jharia coalfield.",
        bbox={"x0": 60, "y0": 150, "x1": 520, "y1": 185},
        section="CMPDI Operational Audit"
    )
    vector_store.add_chunk(
        doc_id="DOC004_GEOLOGICAL_REPORT_2024",
        page_number=28,
        text="Rajmahal opencast output declined in 2023 due to severe slope instability, overburden backlog, and monsoonal flooding in the central pit.",
        bbox={"x0": 60, "y0": 220, "x1": 520, "y1": 255},
        section="ECL Geotechnical Variations"
    )
    vector_store.add_chunk(
        doc_id="DOC001_ANNUAL_REPORT_2024",
        page_number=47,
        text="SECL Gevra project scaled to record 70 MT output enabled by deployment of 42 cum electric rope shovels and 240 tonne dump trucks.",
        bbox={"x0": 70, "y0": 210, "x1": 500, "y1": 235},
        section="SECL Megaprojects"
    )
    print("✓ Indexed Vector Chunks with token bounding-box coordinates.")
    
    # 5. Run Evidence and Consistency Engine
    evidence_engine = EvidenceAndConsistencyEngine(fact_store, vector_store)
    conf_res = evidence_engine.process_consistency_and_conflicts()
    print(f"✓ Evidence Engine: {len(conf_res['supersessions_resolved'])} Supersessions resolved; {len(conf_res['conflicts_flagged'])} Genuine Conflicts flagged for officer review.")
    
    anom_res = evidence_engine.detect_and_explain_anomalies()
    print(f"✓ Anomaly Detector: {len(anom_res)} Statistical Anomalies detected with semantic root-cause explanations.")
    
    # 6. Populate Provenance Graph
    all_current_facts = fact_store.query_facts(include_superseded=True)
    graph_store.populate_from_facts(fact_store.get_all_mines(), all_current_facts)
    print(f"✓ Provenance Graph: {graph_store.graph.number_of_nodes()} Nodes, {graph_store.graph.number_of_edges()} Directed Provenance Relationships.")
    
    print("🎉 MineIntel Data Layer successfully seeded and verified!")

if __name__ == "__main__":
    seed_all()
