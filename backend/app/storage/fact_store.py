import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config import DB_PATH
from .models import FactRecord, MineEntity, DocumentMetadata, DataConflict, AnomalyRecord, ParliamentaryDraft

class FactStore:
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Documents Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                title TEXT,
                doc_type TEXT,
                reporting_period TEXT,
                upload_date TEXT,
                page_count INTEGER,
                file_size_bytes INTEGER,
                source_author TEXT,
                raw_content TEXT
            )
            ''')

            # Mines Master Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mines (
                id TEXT PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                subsidiary TEXT NOT NULL,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                mine_type TEXT,
                operational_status TEXT
            )
            ''')

            # Facts Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                doc_id TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                bbox_json TEXT,
                raw_text TEXT,
                mine_code TEXT NOT NULL,
                mine_name TEXT NOT NULL,
                subsidiary TEXT NOT NULL,
                metric TEXT NOT NULL,
                raw_value REAL NOT NULL,
                raw_unit TEXT NOT NULL,
                normalized_value REAL NOT NULL,
                normalized_unit TEXT NOT NULL,
                fiscal_year TEXT NOT NULL,
                period_type TEXT NOT NULL,
                is_superseded INTEGER DEFAULT 0,
                superseded_by TEXT,
                supersession_reason TEXT,
                has_conflict INTEGER DEFAULT 0,
                conflict_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (doc_id) REFERENCES documents (id),
                FOREIGN KEY (mine_code) REFERENCES mines (code)
            )
            ''')

            # Conflicts Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conflicts (
                id TEXT PRIMARY KEY,
                conflict_type TEXT NOT NULL,
                mine_code TEXT NOT NULL,
                mine_name TEXT NOT NULL,
                metric TEXT NOT NULL,
                fiscal_year TEXT NOT NULL,
                records_json TEXT NOT NULL,
                discrepancy_delta REAL NOT NULL,
                status TEXT NOT NULL,
                resolution_notes TEXT,
                resolved_by TEXT,
                detected_at TEXT NOT NULL
            )
            ''')

            # Anomalies Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                mine_code TEXT NOT NULL,
                mine_name TEXT NOT NULL,
                subsidiary TEXT NOT NULL,
                metric TEXT NOT NULL,
                fiscal_year TEXT NOT NULL,
                current_value REAL NOT NULL,
                historical_avg REAL NOT NULL,
                deviation_pct REAL NOT NULL,
                anomaly_type TEXT NOT NULL,
                explanation TEXT,
                supporting_doc_id TEXT,
                supporting_page INTEGER,
                detected_at TEXT NOT NULL
            )
            ''')

            # Parliamentary Drafts Table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS parliamentary_drafts (
                id TEXT PRIMARY KEY,
                question_no TEXT NOT NULL,
                session TEXT NOT NULL,
                house TEXT NOT NULL,
                ministry TEXT NOT NULL,
                question_text TEXT NOT NULL,
                key_entities_json TEXT,
                time_period TEXT,
                drafted_response TEXT NOT NULL,
                annexure_json TEXT,
                confidence_score REAL,
                evidence_sources_json TEXT,
                approval_status TEXT NOT NULL,
                approved_by TEXT,
                approved_at TEXT
            )
            ''')
            
            # Indexes for ultra-fast queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_mine_metric_year ON facts(mine_code, metric, fiscal_year);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_subsidiary ON facts(subsidiary);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_doc_id ON facts(doc_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conflicts_status ON conflicts(status);")
            conn.commit()

    # Mines CRUD
    def add_mine(self, mine: MineEntity) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO mines (id, code, name, normalized_name, subsidiary, state, district, lat, lng, mine_type, operational_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (mine.id, mine.code, mine.name, mine.normalized_name, mine.subsidiary, mine.state, mine.district, mine.lat, mine.lng, mine.mine_type, mine.operational_status))
            conn.commit()
            return mine.code

    def get_all_mines(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mines ORDER BY subsidiary, name")
            return [dict(row) for row in cursor.fetchall()]

    def get_mine_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mines WHERE code = ? OR normalized_name = ?", (code, code))
            row = cursor.fetchone()
            return dict(row) if row else None

    # Documents CRUD
    def add_document(self, doc: DocumentMetadata, raw_content: str = "") -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO documents (id, filename, file_type, title, doc_type, reporting_period, upload_date, page_count, file_size_bytes, source_author, raw_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (doc.id, doc.filename, doc.file_type, doc.title, doc.doc_type, doc.reporting_period, doc.upload_date, doc.page_count, doc.file_size_bytes, doc.source_author, raw_content))
            conn.commit()
            return doc.id

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_documents(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename, file_type, title, doc_type, reporting_period, upload_date, page_count FROM documents ORDER BY upload_date DESC")
            return [dict(row) for row in cursor.fetchall()]

    # Facts CRUD
    def add_fact(self, fact: FactRecord) -> str:
        fact_id = fact.id or str(uuid.uuid4())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            bbox_str = json.dumps(fact.bbox) if fact.bbox else "{}"
            cursor.execute('''
            INSERT OR REPLACE INTO facts (id, doc_id, doc_type, page_number, bbox_json, raw_text, mine_code, mine_name, subsidiary, metric, raw_value, raw_unit, normalized_value, normalized_unit, fiscal_year, period_type, is_superseded, superseded_by, supersession_reason, has_conflict, conflict_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (fact_id, fact.doc_id, fact.doc_type, fact.page_number, bbox_str, fact.raw_text, fact.mine_code, fact.mine_name, fact.subsidiary, fact.metric, fact.raw_value, fact.raw_unit, fact.normalized_value, fact.normalized_unit, fact.fiscal_year, fact.period_type, 1 if fact.is_superseded else 0, fact.superseded_by, fact.supersession_reason, 1 if fact.has_conflict else 0, fact.conflict_id, fact.created_at))
            conn.commit()
            return fact_id

    def query_facts(self, mine_code: Optional[str] = None, subsidiary: Optional[str] = None, metric: Optional[str] = None, fiscal_year: Optional[str] = None, include_superseded: bool = False) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []
            
            if not include_superseded:
                conditions.append("is_superseded = 0")
            if mine_code:
                conditions.append("(mine_code = ? OR mine_name LIKE ?)")
                params.extend([mine_code, f"%{mine_code}%"])
            if subsidiary:
                conditions.append("subsidiary = ?")
                params.append(subsidiary)
            if metric:
                conditions.append("metric = ?")
                params.append(metric)
            if fiscal_year:
                conditions.append("fiscal_year = ?")
                params.append(fiscal_year)
                
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"SELECT * FROM facts{where_clause} ORDER BY fiscal_year ASC, mine_name ASC"
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["bbox"] = json.loads(d["bbox_json"]) if d.get("bbox_json") else {}
                d["is_superseded"] = bool(d["is_superseded"])
                d["has_conflict"] = bool(d["has_conflict"])
                results.append(d)
            return results

    def mark_fact_superseded(self, old_fact_id: str, new_fact_id: str, reason: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE facts 
            SET is_superseded = 1, superseded_by = ?, supersession_reason = ?
            WHERE id = ?
            ''', (new_fact_id, reason, old_fact_id))
            conn.commit()

    # Conflicts CRUD
    def add_conflict(self, conflict: DataConflict) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO conflicts (id, conflict_type, mine_code, mine_name, metric, fiscal_year, records_json, discrepancy_delta, status, resolution_notes, resolved_by, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (conflict.id, conflict.conflict_type, conflict.mine_code, conflict.mine_name, conflict.metric, conflict.fiscal_year, json.dumps(conflict.records_involved), conflict.discrepancy_delta, conflict.status, conflict.resolution_notes, conflict.resolved_by, conflict.detected_at))
            conn.commit()
            return conflict.id

    def list_conflicts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM conflicts WHERE status = ? ORDER BY detected_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM conflicts ORDER BY detected_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["records_involved"] = json.loads(d["records_json"]) if d.get("records_json") else []
                results.append(d)
            return results

    def resolve_conflict(self, conflict_id: str, chosen_record_id: str, resolution_notes: str, resolved_by: str = "Officer In-Charge"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE conflicts 
            SET status = 'resolved', resolution_notes = ?, resolved_by = ?
            WHERE id = ?
            ''', (resolution_notes, resolved_by, conflict_id))
            
            # Retrieve conflict records
            cursor.execute("SELECT records_json FROM conflicts WHERE id = ?", (conflict_id,))
            row = cursor.fetchone()
            if row:
                records = json.loads(row["records_json"])
                for rec in records:
                    rec_id = rec.get("id")
                    if rec_id == chosen_record_id:
                        cursor.execute("UPDATE facts SET is_superseded = 0, has_conflict = 0 WHERE id = ?", (rec_id,))
                    else:
                        cursor.execute("UPDATE facts SET is_superseded = 1, supersession_reason = ?, has_conflict = 0 WHERE id = ?", (f"Manual resolution: superseded by {chosen_record_id} ({resolution_notes})", rec_id))
            conn.commit()

    # Anomalies CRUD
    def add_anomaly(self, anomaly: AnomalyRecord) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO anomalies (id, mine_code, mine_name, subsidiary, metric, fiscal_year, current_value, historical_avg, deviation_pct, anomaly_type, explanation, supporting_doc_id, supporting_page, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (anomaly.id, anomaly.mine_code, anomaly.mine_name, anomaly.subsidiary, anomaly.metric, anomaly.fiscal_year, anomaly.current_value, anomaly.historical_avg, anomaly.deviation_pct, anomaly.anomaly_type, anomaly.explanation, anomaly.supporting_doc_id, anomaly.supporting_page, anomaly.detected_at))
            conn.commit()
            return anomaly.id

    def list_anomalies(self, mine_code: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if mine_code:
                cursor.execute("SELECT * FROM anomalies WHERE mine_code = ? ORDER BY fiscal_year DESC", (mine_code,))
            else:
                cursor.execute("SELECT * FROM anomalies ORDER BY detected_at DESC")
            return [dict(r) for r in cursor.fetchall()]

    # Parliamentary Drafts CRUD
    def save_parliamentary_draft(self, draft: ParliamentaryDraft) -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT OR REPLACE INTO parliamentary_drafts (id, question_no, session, house, ministry, question_text, key_entities_json, time_period, drafted_response, annexure_json, confidence_score, evidence_sources_json, approval_status, approved_by, approved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (draft.id, draft.question_no, draft.session, draft.house, draft.ministry, draft.question_text, json.dumps(draft.key_entities), draft.time_period, draft.drafted_response, json.dumps(draft.annexure_table), draft.confidence_score, json.dumps(draft.evidence_sources), draft.approval_status, draft.approved_by, draft.approved_at))
            conn.commit()
            return draft.id

    def list_parliamentary_drafts(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parliamentary_drafts ORDER BY id DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["key_entities"] = json.loads(d["key_entities_json"]) if d.get("key_entities_json") else []
                d["annexure_table"] = json.loads(d["annexure_json"]) if d.get("annexure_json") else []
                d["evidence_sources"] = json.loads(d["evidence_sources_json"]) if d.get("evidence_sources_json") else []
                results.append(d)
            return results
