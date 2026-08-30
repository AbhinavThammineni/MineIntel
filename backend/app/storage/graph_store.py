import networkx as nx
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..config import GRAPH_DB_PATH

class MiningGraphStore:
    def __init__(self, storage_path=None):
        self.storage_path = Path(storage_path or GRAPH_DB_PATH)
        self.graph = nx.DiGraph()
        self.load()

    def load(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception:
                self.graph = nx.DiGraph()
        else:
            self.graph = nx.DiGraph()

    def save(self):
        data = nx.node_link_data(self.graph)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_hierarchy_node(self, node_id: str, label: str, node_type: str, properties: Optional[Dict[str, Any]] = None):
        self.graph.add_node(node_id, label=label, type=node_type, **(properties or {}))

    def add_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None):
        self.graph.add_edge(source_id, target_id, rel=rel_type, **(properties or {}))

    def populate_from_facts(self, mines: List[Dict[str, Any]], facts: List[Dict[str, Any]]):
        # Root node: Coal India Limited (CIL)
        self.graph.add_node("CIL", label="Coal India Limited", type="Organization")

        # Subsidiary nodes
        subsidiaries = set(m.get("subsidiary") for m in mines if m.get("subsidiary"))
        for sub in subsidiaries:
            sub_id = f"SUB_{sub}"
            self.graph.add_node(sub_id, label=sub, type="Subsidiary")
            self.graph.add_edge("CIL", sub_id, rel="HAS_SUBSIDIARY")

        # Mine nodes
        for mine in mines:
            m_code = mine["code"]
            sub_id = f"SUB_{mine['subsidiary']}"
            self.graph.add_node(m_code, label=mine["name"], type="Mine", state=mine["state"], district=mine["district"], lat=mine["lat"], lng=mine["lng"])
            self.graph.add_edge(sub_id, m_code, rel="OPERATES_MINE")

        # Fact and Evidence nodes
        for fact in facts:
            m_code = fact["mine_code"]
            f_id = f"FACT_{fact['id']}"
            doc_id = f"DOC_{fact['doc_id']}"
            
            # Fact node
            self.graph.add_node(
                f_id,
                label=f"{fact['metric']}: {fact['normalized_value']} {fact['normalized_unit']}",
                type="FactRecord",
                metric=fact["metric"],
                value=fact["normalized_value"],
                unit=fact["normalized_unit"],
                fiscal_year=fact["fiscal_year"],
                is_superseded=fact.get("is_superseded", False)
            )
            
            # Connect Mine to Fact
            self.graph.add_edge(m_code, f_id, rel="HAS_METRIC_FACT", year=fact["fiscal_year"], metric=fact["metric"])
            
            # Document Node
            self.graph.add_node(doc_id, label=fact.get("doc_id", "DOC"), type="Document", doc_type=fact.get("doc_type", "Report"))
            
            # Connect Fact to Document Evidence
            self.graph.add_edge(f_id, doc_id, rel="EVIDENCE_FROM", page=fact.get("page_number", 1), bbox=fact.get("bbox", {}))
            
            # If superseded, link to superseding fact
            if fact.get("is_superseded") and fact.get("superseded_by"):
                sup_fact_id = f"FACT_{fact['superseded_by']}"
                self.graph.add_edge(sup_fact_id, f_id, rel="SUPERSEDES", reason=fact.get("supersession_reason", ""))

        self.save()

    def get_mine_lineage(self, mine_code: str) -> Dict[str, Any]:
        if mine_code not in self.graph:
            return {"error": f"Mine {mine_code} not found in graph"}

        parents = [p for p in self.graph.predecessors(mine_code)]
        facts = []
        for successor in self.graph.successors(mine_code):
            node_data = self.graph.nodes[successor]
            edge_data = self.graph.get_edge_data(mine_code, successor)
            
            # Find evidence doc for this fact
            evidence = []
            for doc_succ in self.graph.successors(successor):
                doc_node = self.graph.nodes[doc_succ]
                doc_edge = self.graph.get_edge_data(successor, doc_succ)
                evidence.append({
                    "doc_id": doc_succ,
                    "doc_type": doc_node.get("doc_type"),
                    "page": doc_edge.get("page"),
                    "bbox": doc_edge.get("bbox")
                })

            facts.append({
                "fact_id": successor,
                "data": node_data,
                "relationship": edge_data,
                "evidence": evidence
            })

        return {
            "mine": self.graph.nodes[mine_code],
            "subsidiary": parents[0] if parents else None,
            "facts_lineage": facts
        }

    def trace_subsidiary_mines(self, subsidiary_code: str) -> List[Dict[str, Any]]:
        sub_id = f"SUB_{subsidiary_code}" if not subsidiary_code.startswith("SUB_") else subsidiary_code
        if sub_id not in self.graph:
            return []
        
        mines = []
        for mine_node in self.graph.successors(sub_id):
            m_data = self.graph.nodes[mine_node]
            mines.append({
                "code": mine_node,
                "name": m_data.get("label"),
                "state": m_data.get("state"),
                "district": m_data.get("district")
            })
        return mines
