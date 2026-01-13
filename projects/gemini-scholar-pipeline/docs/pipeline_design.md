# Theological Research Pipeline - PRD (v2.0)

## Product Requirements Document
**Version:** 2.1  
**Date:** 2025-12-12  
**Status:** Production (v2.1 Update)

---

## 1. 개요

### 1.1 목적
Gemini와 Google Scholar를 결합하여 **"자율적으로 사실을 검증하고 심화 연구를 수행하는"** 에이전트 시스템 구축. 단순 생성이 아닌, **증거(Fact)**에 기반한 글쓰기 구현.

### 1.2 핵심 가치 (v2.1)
- **Hybrid Capability**: 무료(Standard) 운용과 유료(Deep API) 운용의 유연한 전환.
- **Zero Hallucination**: DB에 존재하는 Fact가 아니면 쓰지 않음.
- **Auto-Research**: 정보가 부족하면 스스로 검색 루프를 돌림.
- **Evidence Trace**: 모든 문장에 대한 출처(ID) 추적 및 검증.
- **Persistent Knowledge**: 연구할수록 쌓이는 개인화된 SQLite 지식베이스.

---

## 2. 파이프라인 아키텍처 (v2.0)

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: Knowledge Acquisition (지식 획득)                     │
│  • [Standard] Scholar Labs Agent (Search) → Markdown Results    │
│  • [Premium] Deep Scholar Agent (API) → Markdown Results        │
│  • KB Manager (Ingestion) → SQLite DB (papers table)            │
│  • Fact Extractor (Extraction) → SQLite DB (facts table)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1.5: Web Reference Ingestion (Knowledge Expansion)       │
│  • Objective: Phase 1 리포트에서 인용된 웹 소스(URL)를 실질적인 지식으로 데이터베이스화. │
│  • Process:                                                     │
│    1. `web_ingestor.py`가 `_raw.md`를 파싱하여 URL 목록 추출.   │
│    2. Playwright로 각 URL 방문하여 본문 텍스트 수집 (PDF는 메타데이터 위주). │
│    3. `kb_manager.py`를 통해 `scholar_kb.db`에 적재 (`source_type='web_reference'`). │
│  • Output: `scholar_kb.db` (Expanded with web data)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: Evidence-Based Writing (Recursive & Grounded)         │
│  • Retrieve Facts (RAG Lite)                                    │
│  • IF insufficient facts → Trigger Phase 1 (Recursive)          │
│  • ELSE → Generate Draft with Citations (Gemini)                │
│  • 출력: draft_section.md (with (Source: [ID]) tags)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 3: Verification & Polish                                 │
│  • Citation Verifier: 리포트 내 [ID] vs DB 대조                 │
│  • HTML Visualization: 시각적 리포트 생성                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 상세 명세

### 3.1 Knowledge Base (Phase 1)
- **Storage**: SQLite (`scholar_kb.db`)
- **Schema**:
    - `papers`: 논문 메타데이터, 원문(Markdown)
    - `facts`: 추출된 주장(Claim), 근거(Evidence), 통계(Stats)
- **Ingestion**: `kb_manager.py`가 `results/` 폴더의 마크다운 파일을 파싱하여 DB 적재.

### 3.2 Fact Extraction (Phase 1)
- **Module**: `fact_extractor.py`
- **Logic**: 논문 텍스트를 LLM에게 주고 "인용할 만한 사실"을 JSON으로 추출.
- **Output**: `facts` 테이블에 저장 (Source ID, Content, Context).

### 3.3 Evidence Writer (Phase 2)
- **Module**: `evidence_writer.py`
- **Logic**:
    1. 주제 키워드로 `facts` 테이블 검색.
    2. 사실이 < 3개면 `scholar_labs_agent.py` 실행 (Auto-Research).
    3. 확보된 사실을 프롬프트에 주입하여 글쓰기.
- **Constraints**: "DB에 있는 사실만 사용할 것", "문장마다 Source ID 표기".

### 3.4 Verification (Phase 3)
- **Module**: `citation_verifier.py`
- **Logic**: 정규식으로 `(Source: [ID])` 추출 후 DB 존재 여부 확인.
- **Output**: Verification Report (Valid/Invalid Count).

---

## 4. 파일 구조 (v2.0)

```
google-scholar-agent/
├── evidence_writer.py      # [Main] 증거 기반 작가 (재귀 루프 포함)
├── fact_extractor.py       # [Core] 팩트 추출기
├── kb_manager.py           # [Core] DB 관리자
├── citation_verifier.py    # [Tools] 인용 검증기
├── scholar_labs_agent.py   # [Agent] 검색 에이전트
├── visualize_session.py    # [Tools] HTML 시각화
├── scholar_kb.db           # [Data] 지식베이스 (SQLite)
└── reports/                # 결과물 저장소
```

---

## 5. 버전 히스토리

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0 | 2025-12-05 | 초기 파이프라인 (Pipeline.sh 위주) |
| 1.7 | 2025-12-05 | 시각화 모듈 추가 |
| 2.0 | 2025-12-11 | **Recursive Research Loop** 및 **SQLite KB** 도입 |

