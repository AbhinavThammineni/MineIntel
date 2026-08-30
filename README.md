# ⛏️ MineIntel — Enterprise Mining Intelligence & Evidence Engine

<div align="center">

[![Live Deployment](https://img.shields.io/badge/Vercel-Live%20Platform-emerald?style=for-the-badge&logo=vercel)](https://mine-intel.vercel.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-AbhinavThammineni%2FMineIntel-blue?style=for-the-badge&logo=github)](https://github.com/AbhinavThammineni/MineIntel)
[![Python FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Leaflet GIS](https://img.shields.io/badge/Leaflet-GIS%20Mapping-199900?style=for-the-badge&logo=leaflet)](https://leafletjs.com)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)

**An evidence-based, mathematically grounded intelligence platform for Indian coal mining statutory filings, parliamentary drafts, geospatial telemetry, and automated consistency auditing.**

[🚀 Explore Live Platform](https://mine-intel.vercel.app) • [📖 Architecture & Core Flow](#-core-8-word-architecture) • [✨ Key Modules](#-platform-modules) • [🔐 Security & RBAC](#-government-rbac--officer-sign-off)

---

</div>

## 📌 Problem Statement & Overview

Government ministries, regulatory authorities, and mining enterprises (such as **Coal India Limited**, **Ministry of Coal**, and its subsidiaries) manage thousands of pages of unstructured statutory filings, monthly flash figures, geological survey reports, and annual audited accounts. 

Standard LLM RAG pipelines often suffer from:
1. **Hallucinated figures and incorrect mathematical trends (CAGR/percentages)**.
2. **Lack of verifiable provenance or visual bounding-box evidence**.
3. **Data conflicts between provisional flash estimates and audited annual accounts**.
4. **Governance risks where unauthorized roles could approve parliamentary statements**.

**MineIntel solves this with a multi-store deterministic engine that blends SQL fact tables, pgvector semantic search, Neo4j knowledge lineage, and human-in-the-loop statutory sign-offs.**

---

## ⚡ Core 8-Word Architecture

MineIntel operates on a deterministic, audit-proof data pipeline:

$$\text{READ} \longrightarrow \text{UNDERSTAND} \longrightarrow \text{EXTRACT} \longrightarrow \text{CLEAN} \longrightarrow \text{STORE} \longrightarrow \text{VERIFY} \longrightarrow \text{ANSWER} \longrightarrow \text{REPORT}$$

```mermaid
graph LR
    A[1. Ingest Documents<br/>PDF/Scans/Excel] --> B[2. Token Bounding Boxes<br/>OCR & Structure]
    B --> C[3. Data Normalization<br/>Unit Canonicalization]
    C --> D[4. Multi-Store Persistence<br/>SQL + Vector + Graph]
    D --> E[5. Consistency Engine<br/>Supersession & Conflict Triage]
    E --> F[6. Deterministic Math<br/>CAGR & Annexures]
    F --> G[7. Evidence UI & GIS<br/>19 Coalfields & Bounding Boxes]
    G --> H[8. RBAC Approval<br/>Parliamentary Sign-Off]
```

---

## ✨ Platform Modules

### 1. 🛡️ Evidence-Backed Q&A Assistant
- **Deterministic Compute:** Mathematical queries (e.g., CAGR, growth percentages, year-over-year production comparisons) are calculated via verified Python routines—never estimated by raw language models.
- **Visual Bounding-Box Provenance:** Every response includes high-confidence citation badges linking directly to the statutory document, page number, and highlighted bounding box.

### 2. 🗺️ Geospatial Mine Command & Anomaly Map
- **19 Major Indian Coalfields:** Interactive GIS tracking across SECL (Gevra, Kusmunda, Dipka), MCL (Lakhanpur, Bhubaneswari), NCL (Jayant, Nigahi), CCL (Amrapali, Ashoka, Piparwar), ECL (Rajmahal, Sonepur Bazari), BCCL (Block II, Kusunda, Moonidih), and WCL (Penganga, Umrer).
- **Live Mine Telemetry Drawer:** Tapping any mine marker reveals historical output trajectories (FY 2021-22 to FY 2024-25), overburden removal ($MCuM$) stripping rates, operational status, and document audit records.
- **100% Free Global Tiles:** High-speed OpenStreetMap CDN integration with zero API keys or watermarks.

### 3. 📊 Automated 6-Part Statutory Report Builder
- Compiles complete statutory intelligence reports in 1 click across 6 formal sections:
  1. **Executive Summary**
  2. **Subsidiary Production & Deterministic CAGR Matrix**
  3. **Overburden Removal ($MCuM$) Matrix**
  4. **State-Wise Resource & Output Allocation**
  5. **Operational Anomalies & Root-Cause Log**
  6. **Data Consistency & Supersession Audit Trail**
- Built-in **Print / PDF export** functionality formatted for official ministry distribution.

### 4. 🏛️ Parliamentary Question & Statement Engine (with RBAC)
- Drafts formal **Lok Sabha & Rajya Sabha** ministry replies with auto-compiled **Annexure-I** tables.
- **Officer e-Sign Gateway:** Role-based access control protecting approvals.
  - **Analyst Role (`View-Only`):** Can query, inspect data, and preview drafted statements.
  - **Approving Officer (`Under Secretary`):** Authenticates via Security PIN (`1234`) to apply the statutory digital seal.
- **Instant Statement Collapse:** Prominent close actions at both top and bottom of draft cards without requiring page reloads.

### 5. ⚖️ Evidence Consistency & Conflict Triage Center
- **Automated Supersession:** Automatically reconciles provisional flash reports (Authority Rank 30) when final audited annual filings (Authority Rank 100) are released, maintaining complete historical audit lineage.
- **Genuine Conflict Triage:** When equal-ranked statutory filings differ, the system avoids guessing and raises an interactive discrepancy triage card for human officer sign-off.

### 6. 📱 Mobile-First Responsive Design
- Optimized for desktop, tablets, and smartphones ($360\text{px} - 414\text{px}$).
- Uses responsive touch cards for parliamentary archives and conflict logs with zero horizontal clipping.
- Smooth horizontal swipe wrappers for all data tables (`Swipe table ➔`).
- Automatic smooth-scrolling to the GIS drawer upon marker selection on mobile.

---

## 🔐 Government RBAC & Officer Sign-Off

To ensure strict statutory governance, approvals follow a cryptographic role-based model:

| Role | Access Level | Capabilities | PIN Required |
| :--- | :--- | :--- | :---: |
| **Mining Analyst** | `View-Only` | Query facts, inspect GIS map, generate preview drafts | ❌ No |
| **Under Secretary (Coal Operations)** | `Authorized Approver` | Statutorily approve, digitally sign, and archive official statements | ✅ Demo PIN: `1234` |

---

## 📂 Project Structure

```text
MineIntel/
├── api/
│   └── index.py                    # Vercel Serverless entrypoint (/tmp storage handler)
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_qa.py        # Verified Q&A & Math Compute Endpoints
│   │   │   ├── routes_gis.py       # GIS Map & 19 Mines Telemetry API
│   │   │   ├── routes_reports.py   # 6-Part Automated Report Builder API
│   │   │   ├── routes_parliament.py# Parliamentary Drafts & Sign-Off API
│   │   │   ├── routes_conflicts.py # Supersession & Discrepancy Triage API
│   │   │   └── routes_ingest.py    # Document Extraction Pipeline API
│   │   ├── engine/
│   │   │   ├── analytics_engine.py # Deterministic CAGR & Statistical Analytics
│   │   │   └── consistency_engine.py# Automated Supersession & Conflict Logic
│   │   ├── storage/
│   │   │   ├── fact_store.py       # SQLite / PostgreSQL Relational Store
│   │   │   ├── vector_store.py     # pgvector Semantic Passage Embeddings
│   │   │   └── graph_store.py      # Neo4j Entity & Document Provenance Graph
│   │   ├── config.py               # Environment & Vercel /tmp Path Config
│   │   └── main.py                 # FastAPI Application & Exception Handler
│   └── data/
│       ├── mineintel_facts.db      # Pre-seeded SQLite database with 19 mines
│       ├── mineintel_graph.json    # Lineage knowledge graph
│       └── mineintel_vectors.json  # Semantic vector embeddings
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css          # High-tech glassmorphism & mobile styling
│   │   └── js/
│   │       ├── app.js              # Core UI controller & responsive cards
│   │       ├── gis_map.js          # Leaflet GIS controller (OpenStreetMap CDN)
│   │       ├── parliament_draft.js # RBAC gateway & statement collapse
│   │       ├── report_generator.js # 6-section report compiler
│   │       └── doc_viewer.js       # Bounding-box viewer modal (multi-trigger close)
│   └── index.html                  # Main responsive single-page application
├── requirements.txt                # Production Python dependencies
├── vercel.json                     # Vercel routing & serverless configuration
└── README.md                       # Comprehensive documentation
```

---

## 🚀 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AbhinavThammineni/MineIntel.git
cd MineIntel
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run FastAPI Backend & Frontend
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Open your browser at `http://localhost:8000` to interact with the full dashboard.

---

## 🌐 Cloud Deployment (Vercel)

MineIntel is configured for **1-click serverless deployment** on Vercel:
- Automatically redirects static assets from `/frontend`
- Mounts FastAPI backend endpoints via `api/index.py`
- Handles read-only cloud filesystem constraints by seamlessly caching runtime data in writable `/tmp/mineintel_data`.

**Live Production URL:** [https://mine-intel.vercel.app](https://mine-intel.vercel.app)

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use and extend for enterprise mining intelligence and statutory compliance applications.
