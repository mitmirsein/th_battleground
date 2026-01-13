# Theological Research Pipeline - Architecture Document (v2.0)

**Version:** 2.1  
**Last Updated:** 2025-12-12  
**Status:** Production

---

## 1. Overview

학술 신학 연구를 위한 **자율 재귀 연구(Autonomous Recursive Research)** 및 **증거 기반 저술(Evidence-Based Writing)** 시스템.

### 1.1 Core Improvements (v2.1)
- **Deep Research Integration**: Gemini Deep Research API를 활용한 프리미엄 심층 연구 지원.
- **Hybrid Pipeline**: Standard(무료) 모드와 Deep(유료) 모드 선택적 운용 가능.
- **Persistent Knowledge**: DB에 지식을 축적하여 지속적으로 똑똑해짐.
- **Fact-Based Generation**: "DB에 없는 말은 하지 않는다" (Zero Hallucination).
- **Closed-Loop Verification**: 생성된 인용구를 역추적하여 검증.

### 1.2 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Knowledge Acquisition (지식 수집)                 │
│  • Agent: Scholar Labs Semantic Search                      │
│  • Ingest: Markdown Results → SQLite DB                     │
│  • Extract: Unstructured Text → Atomic Facts (JSON)         │
│  Output: scholar_kb.db (papers, facts tables)               │
└─────────────────────────────────────────────────────────────┘
                               ↓ (Recursive if needed)
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Evidence-Based Writing (저술)                     │
│  • Logic: Retrieve Facts → Draft Paragraphs                 │
│  • Constraint: Must cite [Source: ID] for every claim       │
│  Output: draft_section.md                                   │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Deep Verification (검증)                          │
│  • Audit: Check Generated IDs vs DB Records                 │
│  Output: Verification Report (integrity score)              │
└─────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Output Visualization                              │
│  • Render: Markdown → HTML + Interactive Citations          │
│  Output: html reports                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Module Architecture

### 2.1 Core Modules (v2.0)

| 모듈 | 파일 | 역할 |
|------|------|------|
| **Evidence Writer** | `evidence_writer.py` | [Main] 검색-추출-쓰기 순환 루프 제어 |
| **KB Manager** | `kb_manager.py` | [Data] SQLite DB 입출력 관리 |
| **Fact Extractor** | `fact_extractor.py` | [Core] 텍스트에서 Claim/Evidence 추출 |
| **Scholar Agent** | `scholar_labs_agent.py` | [Tool] Google Scholar 검색 수행 (Standard) |
| **Deep Research** | `deep_research_session.py` | [Agent] Gemini Deep Research API 배경 탐구 (Premium) |
| **Deep Scholar** | `scholar_deep_agent.py` | [Agent] Gemini Deep Research API 논문 검색 (Premium) |
| **Web Ingestor** | `web_ingestor.py` | [Tool] Deep Research 웹 레퍼런스 수집-저장 |
| **Citation Verifier** | `citation_verifier.py` | [Audit] 인용 무결성 검증 |
| **Visualizer** | `visualize_session.py` | [UI] HTML 리포트 생성 |

### 2.2 Execution Scripts

| 스크립트 | 용도 |
|----------|------|
| `python web_ingestor.py` | **웹 레퍼런스 수집 (Phase 1.5)** |
| `python evidence_writer.py` | **증거 기반 저술 (핵심)** |
| `python citation_verifier.py` | 인용 검증 |
| `run_visualize.sh` | HTML 시각화 |
| `pipeline.sh` | (Legacy) 전체 일괄 처리 |

---

## 3. Data Flow

### 3.1 Knowledge Flow
```
[Internet] 
    │ (Scholar Agent)        (Web Ingestor)
    ↓                       ↓
[Markdown Files (results/)]   [Web Content]
    │ (KB Manager)          │
    ↓                       ↓
[SQLite DB (papers table: source_type=paper/web)]
    │ (Fact Extractor)
    ↓
[SQLite DB (facts table)]
    │ (Evidence Writer)
    ↓
[Draft Report (Markdown)]
```

### 3.2 Database Schema (`scholar_kb.db`)

#### `papers` Table
- `id`: TEXT (UUID or hash)
- `title`: TEXT
- `content`: TEXT (Full markdown content)
- `url`: TEXT
- `ingested_at`: DATETIME

#### `facts` Table
- `id`: TEXT (8-char hash)
- `paper_id`: TEXT (FK)
- `type`: TEXT (claim, evidence, stat, quote)
- `content`: TEXT (The fact itself)
- `context`: TEXT (Surrounding context for RAG)

---

## 4. Module Details

### 4.1 Evidence Writer (`evidence_writer.py`)
- **역할**: 오케스트레이터. 사용자의 주제를 받아 글을 완성함.
- **알고리즘**:
    1. `facts` 테이블에서 관련 정보 검색 (Keyword/Semantic).
    2. 정보 부족 시(`count < 3`) → `auto_research()` 트리거.
    3. `scholar_labs_agent.py` 호출 → 결과 Ingestion → Fact Extraction.
    4. 충분한 정보 확보 후 Gemini에게 집필 요청 (System Prompt: "Use only provided facts").

### 4.2 Citation Verifier (`citation_verifier.py`)
- **역할**: "이 인용구가 진짜인가?" 판독.
- **로직**:
    - 정규식 `\(Source: \[?([a-zA-Z0-9]+)\]?\)` 매칭.
    - 추출된 ID가 `facts` 테이블이나 `papers` 테이블에 존재하는지 쿼리.
    - 존재하지 않으면 `Invalid` 판정.

---

## 5. Technical Stack
- **Language**: Python 3.10+
- **Database**: SQLite3 (Local file `scholar_kb.db`)
- **Browser**: Playwright (for Scholar Agent & Gemini)
- **Visualization**: Jinja2 + Tailwind CSS

---

## 6. Version History
- **v1.0**: Gemini + Manual Scholar Search
- **v1.5**: Automated Batch Search
- **v2.0**: **Recursive Research Loop** + **SQLite KB** (Current)
