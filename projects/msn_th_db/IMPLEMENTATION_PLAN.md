# 🏗️ Implementation Plan: msn_th_db

> **Project**: msn_th_db (Vector DB 없는 개인 RAG 체계)  
> **Created**: 2026-01-13  
> **Status**: � Implementation Phase 1

---

## 📋 Overview

ChromaDB 기반 Vector DB를 제거하고, 로컬 JSON 아카이브를 MCP Server를 통해 Antigravity가 직접 검색하는 개인 RAG 체계 구축.

---

## 🎯 Goals

1. **Zero-Footprint**: 파일 시스템 + LLM만으로 검색-증강 생성
2. **MCP 네이티브 통합**: Antigravity에서 도구처럼 자연스럽게 사용
3. **인용 정확성**: 청크별 citation 메타데이터로 정밀 인용

---

## 🛠️ 기술 스택

| 구성 요소 | 기술 | 버전/비고 |
|:---|:---|:---|
| **Runtime** | Python 3.11+ | `shared_venv` 사용 |
| **MCP Framework** | `mcp` (Python SDK) | Antigravity 통합 |
| **검색 엔진** | `grep` | macOS 내장 (ripgrep 대체 가능) |
| **PDF 처리** | `PyMuPDF` (fitz) | 텍스트 추출 |
| **데이터 검증** | `Pydantic` | JSON 스키마 |
| **저장 포맷** | JSONL | 1 line = 1 chunk |
| **텍스트 정규화** | `unicodedata` (NFC) | 내장 라이브러리 |

### 의존성 (requirements.txt)

```
mcp>=0.1.0
pydantic>=2.0
PyMuPDF>=1.23
pyyaml>=6.0
```

### 외부 도구

```bash
# 추가 설치 불필요 (macOS 내장)
# 선택: 속도 향상을 위해 ripgrep 설치 가능
# brew install ripgrep
```

---

## 🏛️ 설계 원칙 (Peer Review 반영)

### 핵심 리스크 대응

| 리스크 | 해결책 |
|:---|:---|
| **chunk_id로 파일 못 찾음** | `global_chunk_id` = `{doc_id}:{page}:{seq}` |
| **대형 JSON 반복 로드** | **JSONL 포맷** (1 line = 1 chunk) |
| **page_offset 실수** | `pdf_page` + `printed_page` 동시 저장 |

### 저장 포맷: JSONL

```
msn_th_archive/
├── docs/
│   ├── RGG_4_4.meta.json      # 문서 메타데이터
│   ├── EKL_3_1.meta.json
│   └── ...
├── chunks/
│   ├── RGG_4_4.jsonl          # 청크 (1 line = 1 chunk)
│   ├── EKL_3_1.jsonl
│   └── ...
└── manifest.json              # doc_id → paths 매핑
```

### ID 규칙

| ID 유형 | 포맷 | 예시 |
|:---|:---|:---|
| `doc_id` | `{abbr}_{edition}_{volume}` | `RGG_4_4`, `KD_1_1` |
| `chunk_id` (로컬) | `{page}_{seq}` | `0235_001` |
| `global_chunk_id` | `{doc_id}:{chunk_id}` | `RGG_4_4:0235_001` |

### 페이지 추적 (인용 신뢰성)

```json
{
  "pdf_page": 247,      // 원본 PDF 페이지 (0-based)
  "printed_page": 235,  // offset 적용 후 (인용용)
  "citation": "RGG, 4. Aufl., Bd. IV, 235"
}
```

### MCP 서버 원칙

- **Stateless**: 검색만, LLM 호출 없음
- **결정적**: glossary/룰 기반 확장만 (LLM 확장은 Antigravity가)
- **검색 힌트 제공**: `match_terms`, `match_count` 포함

### Unicode 정규화

- 모든 텍스트는 **NFC 정규화** 후 저장 (macOS 조합형 이슈 방지)
- 검색 시에도 쿼리를 NFC로 정규화

---

## 🔍 검색 아키텍처 (Semantic Search Strategy)

### 핵심 공식

```
키워드 검색 (MCP) + LLM 증강 (Antigravity) = 시맨틱 검색
```

### 역할 분담

| 구성 요소 | 역할 | 검색 방식 |
|:---|:---|:---|
| **MCP Server** | 키워드 검색 (Retrieval) | grep/ripgrep 기반 |
| **Antigravity** | 시맨틱 필터링 (Semantic Ranking) | LLM 판단 |

### 왜 Vector DB가 불필요한가

```
기존 Vector DB RAG:
  Query → Embedding → Vector Similarity → Top-K → LLM 생성

msn_th_db RAG:
  Query → 3중 언어 확장 → Keyword Search → LLM 시맨틱 필터링 → 생성
                                              ↑
                                    Antigravity가 담당
```

**핵심 통찰**: 
- Vector Embedding의 역할 = "의미적으로 유사한 청크 찾기"
- 이 역할을 **Antigravity LLM이 직접 수행** 가능
- 키워드 검색으로 후보군을 넓게 가져오고, LLM이 관련성 판단

### 검색 플로우

```
사용자: "바르트의 칭의론에 대해 알려줘"
         ↓
[Antigravity: 쿼리 분석]
→ 핵심 개념: 칭의, Barth
→ 3중 언어 확장: ["칭의", "Justification", "Rechtfertigung", "Barth"]
         ↓
[MCP: /msn_th_db:search]
→ grep으로 JSON 아카이브 스캔
→ 매칭 청크 20-50개 반환 (snippet + citation)
         ↓
[Antigravity: 시맨틱 필터링]
→ "이 청크들 중 바르트의 칭의론과 직접 관련된 것은?"
→ Top 5-10 선별
         ↓
[Antigravity: 증강 생성]
→ 선별된 청크 기반 답변 생성
→ 인용: "RGG, 4. Aufl., Bd. IV, 235 참조"
```

### LLM 모델 설정

- **별도 모델 로딩 불필요**: Antigravity 자체가 LLM
- **MCP Server는 stateless**: 순수 검색 기능만 수행
- **시맨틱 판단은 Antigravity에 위임**: 청크 관련성, 요약, 종합 모두 LLM 역할

---

## 📁 Project Structure

```
MS_Dev.nosync/
├── projects/
│   └── msn_th_db/                       # 이 프로젝트
│       ├── IMPLEMENTATION_PLAN.md       # 이 문서 (PRD)
│       ├── src/
│       │   ├── server.py                # MCP Server 메인
│       │   ├── searcher.py              # 검색 로직 (rg 기반)
│       │   ├── chunker.py               # Main Chunking 스크립트
│       │   └── models.py                # Pydantic 데이터 모델
│       ├── config/
│       │   ├── known_sources.yaml       # Known Sources DB
│       │   ├── chunking_presets.yaml    # 청킹 프리셋
│       │   └── glossary.json            # 3중 언어 용어 사전
│       ├── temp/                        # Pre-Chunk 설정 임시 저장
│       └── requirements.txt
│
├── Theology_AI_Lab_v4/
│   └── 01_Library/
│       └── archive/                     # 기존 JSON 데이터 (테스트용)
│
└── data/
    └── msn_th_archive/                  # JSONL 아카이브
        ├── docs/                        # 문서 메타데이터
        │   ├── RGG_4_4.meta.json
        │   └── EKL_3_1.meta.json
        ├── chunks/                      # 청크 데이터 (JSONL)
        │   ├── RGG_4_4.jsonl
        │   └── EKL_3_1.jsonl
        └── manifest.json                # doc_id → paths 매핑
```

---

## 🔧 Phase 1: MCP Server 기본 구조

### 1.1 MCP Server 스켈레톤

**파일**: `src/server.py`

```python
# MCP Server for Theology Archive
# Tools: search, get_chunk, cite, list_sources

from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("msn_th_db")

@app.tool()
async def search(query: str, languages: list = ["ko", "en", "de"], 
                 source: str = None, limit: int = 10) -> list:
    """3중 언어 확장 검색"""
    pass

@app.tool()
async def get_chunk(chunk_id: str) -> dict:
    """특정 청크 전체 내용 반환"""
    pass

@app.tool()
async def cite(chunk_id: str) -> str:
    """인용 포맷 반환"""
    pass

@app.tool()
async def list_sources() -> list:
    """사용 가능한 소스 목록"""
    pass
```

### 1.2 검색 로직

**파일**: `src/searcher.py`

```python
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

class ArchiveSearcher:
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path
        self.sources = self._load_sources()
    
    def expand_query(self, query: str, languages: List[str]) -> List[str]:
        """3중 언어 확장 (glossary 기반 또는 LLM 위임)"""
        # TODO: theological_glossary.json 연동
        return [query]  # 기본: 원본만
    
    def grep_search(self, terms: List[str], source: Optional[str] = None) -> List[Dict]:
        """grep 기반 JSON 검색"""
        results = []
        pattern = "|".join(terms)
        
        target = self.archive_path
        if source:
            target = self.archive_path / f"{source}*.json"
        
        # ripgrep 사용 (빠름)
        cmd = ["rg", "-i", "-l", pattern, str(target)]
        # ... 구현
        
        return results
    
    def load_chunk(self, file_path: Path, chunk_id: str) -> Optional[Dict]:
        """JSON에서 특정 청크 로드"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for chunk in data.get("chunks", []):
            if chunk.get("id") == chunk_id:
                return {
                    "chunk": chunk,
                    "metadata": data.get("metadata", {})
                }
        return None
```

### 1.3 Antigravity 설정

**파일**: `~/.gemini/settings.json` (또는 해당 위치)

```json
{
  "mcpServers": {
    "msn_th_db": {
      "command": "python",
      "args": ["/Users/msn/Desktop/MS_Dev.nosync/projects/msn_th_db/src/server.py"],
      "env": {}
    }
  }
}
```

---

## 🔧 Phase 2: 검색 도구 구현

### 2.1 search 도구

**입력**:
```json
{
  "query": "칭의",
  "languages": ["ko", "en", "de"],
  "source": "RGG",
  "limit": 10
}
```

**출력**:
```json
{
  "results": [
    {
      "global_chunk_id": "RGG_4_4:0235_001",
      "doc_id": "RGG_4_4",
      "chunk_id": "0235_001",
      "printed_page": 235,
      "citation": "RGG, 4. Aufl., Bd. IV, 235",
      "snippet": "Rechtfertigung. I. Religionsgeschichtlich...",
      "match_terms": ["Rechtfertigung"],
      "match_count": 3,
      "match_field": "content"
    }
  ],
  "expanded_queries": ["칭의", "Justification", "Rechtfertigung"],
  "total_matches": 15
}
```

### 2.2 get_chunk 도구

**입력**: `{"global_chunk_id": "RGG_4_4:0235_001"}`

**출력**:
```json
{
  "global_chunk_id": "RGG_4_4:0235_001",
  "doc_id": "RGG_4_4",
  "pdf_page": 247,
  "printed_page": 235,
  "content": "(전체 청크 텍스트)",
  "citation": "RGG, 4. Aufl., Bd. IV, 235",
  "themes": ["칭의", "Justification", "Rechtfertigung"],
  "metadata": {
    "abbr": "RGG",
    "volume": 4,
    "edition": 4
  }
}
```

### 2.3 list_sources 도구

**출력**:
```json
{
  "sources": [
    {
      "doc_id": "RGG_4_4",
      "abbr": "RGG",
      "title": "Religion in Geschichte und Gegenwart",
      "volume": 4,
      "edition": 4,
      "language": "de",
      "doc_type": "dictionary_large",
      "total_chunks": 850,
      "file_path": "chunks/RGG_4_4.jsonl"
    }
  ]
}
```

---

## 🔧 Phase 3: 파일럿 테스트

### 3.1 테스트 대상

- **위치**: `Theology_AI_Lab_v4/01_Library/archive/`
- **파일**: `Evangelisches Kirchenlexikon_EKL1 A-F_OCR.json`

### 3.2 테스트 시나리오

1. MCP Server 시작
2. Antigravity에서 `/msn_th_db:list_sources` 호출
3. `/msn_th_db:search query="Abendmahl"` 테스트
4. 결과 청크 ID로 `get_chunk` 테스트
5. `cite` 테스트

---

## 🔧 Phase 4: 청킹 파이프라인 (PRD)

### 4.0 실행 환경

| 단계 | 환경 | 이유 |
|:---|:---|:---|
| **Pre-Chunking** | Antigravity 대화 | 메타데이터 HITL |
| **Main Chunking** | 로컬 Python (`shared_venv`) | OCR 완료 상태, GPU 불필요 |

### 4.1 Pre-Chunking 워크플로우

```
[PDF 파일 지정]
       ↓
[파일명 파싱] → Known Sources DB 조회
       ↓
[매칭 결과]
  ├─ ✅ 매칭 성공 → DB에서 메타데이터 로드
  └─ ⚠️ 매칭 실패 → AI 추출 시도 (OCR 첫 10페이지)
       ↓
[신뢰도와 함께 제안 표시]
  ┌─────────────────────────────────────────┐
  │ 📄 Detected: RGG_Vol4.pdf               │
  │ ─────────────────────────────────────── │
  │ title: Religion in Geschichte...  ✅ DB │
  │ abbr: RGG                         ✅ DB │
  │ volume: 4                         ✅ 파싱│
  │ edition: 4                        ⚠️ 추정│
  │ language: de                      ✅ DB │
  │ chunk_size: 4000                  ✅ 프리셋│
  │ page_offset: ?                    ❌ 입력필요│
  └─────────────────────────────────────────┘
       ↓
[사용자 확인/수정] ← Antigravity 대화
  • page_offset 입력 (필수)
  • 기타 필드 수정 (선택)
       ↓
[설정 JSON 생성] → temp/pre_chunk_config.json
```

### 4.2 Known Sources Database

```yaml
# config/known_sources.yaml
sources:
  # === 독일어 사전류 ===
  RGG:
    full_title: "Religion in Geschichte und Gegenwart"
    language: de
    doc_type: dictionary_large
    editions:
      4: { year_range: [1998, 2007], volumes: 8 }
      3: { year_range: [1957, 1965], volumes: 7 }
    chunk_preset: dictionary_large
    citation_template: "{abbr}, {ed}. Aufl., Bd. {vol}, {page}"

  TRE:
    full_title: "Theologische Realenzyklopädie"
    language: de
    doc_type: dictionary_large
    editions:
      1: { year_range: [1977, 2007], volumes: 36 }
    chunk_preset: dictionary_large
    citation_template: "{abbr}, Bd. {vol}, {page}"

  EKL:
    full_title: "Evangelisches Kirchenlexikon"
    language: de
    doc_type: dictionary_small
    editions:
      3: { year_range: [1986, 1997], volumes: 5 }
    chunk_preset: dictionary_small
    citation_template: "{abbr}, {ed}. Aufl., Bd. {vol}, {page}"

  HWPh:
    full_title: "Historisches Wörterbuch der Philosophie"
    language: de
    doc_type: dictionary_large
    editions:
      1: { year_range: [1971, 2007], volumes: 13 }
    chunk_preset: dictionary_large
    citation_template: "{abbr}, Bd. {vol}, {page}"

  ThWAT:
    full_title: "Theologisches Wörterbuch zum Alten Testament"
    language: de
    doc_type: lexicon
    chunk_preset: lexicon
    citation_template: "{abbr}, Bd. {vol}, {page}"

  EWNT:
    full_title: "Exegetisches Wörterbuch zum Neuen Testament"
    language: de
    doc_type: lexicon
    chunk_preset: lexicon
    citation_template: "{abbr}, Bd. {vol}, {page}"

  # === 영어 사전류 ===
  TDNT:
    full_title: "Theological Dictionary of the New Testament"
    language: en
    doc_type: lexicon
    editions:
      1: { year_range: [1964, 1976], volumes: 10 }
    chunk_preset: lexicon
    citation_template: "{abbr}, Vol. {vol}, {page}"

  # === 단행본 ===
  KD:
    full_title: "Kirchliche Dogmatik"
    author: "Karl Barth"
    language: de
    doc_type: monograph
    chunk_preset: monograph
    citation_template: "Barth, {abbr} {vol}/{part}, {page}"

  # === 주석서 ===
  BK:
    full_title: "Biblischer Kommentar"
    language: de
    doc_type: commentary
    chunk_preset: commentary
    citation_template: "{abbr}, {page}"

  EKK:
    full_title: "Evangelisch-Katholischer Kommentar"
    language: de
    doc_type: commentary
    chunk_preset: commentary
    citation_template: "{abbr}, {page}"
```

### 4.3 Main Chunking 워크플로우

```
[Pre-Chunk 설정 로드] ← temp/pre_chunk_config.json
       ↓
[PDF 텍스트 추출] ← PyMuPDF (fitz)
       ↓
[텍스트 정제] ← clean_ocr_text()
       ↓
[페이지 매핑] ← page_offset 적용
       ↓
[텍스트 분할] ← chunk_size + overlap
       ↓
[청크별 메타데이터 생성]
  • global_chunk_id: {doc_id}:{page}_{seq}
  • citation: 언어별 템플릿 적용
       ↓
[JSONL 생성] → data/msn_th_archive/chunks/{doc_id}.jsonl
```

### 4.4 OCR 텍스트 정제 (최소)

EKL 테스트 결과, OCR 품질 ~85-90%. 주요 노이즈: 한자 오인식 (`ß` → `公` 등)

```python
def clean_ocr_text(text: str) -> str:
    """최소 OCR 정제 (검색 품질 보장)"""
    import unicodedata
    import re
    
    # 1. NFC 정규화 (macOS 조합형 이슈 방지)
    text = unicodedata.normalize("NFC", text)
    
    # 2. CJK 한자 오인식 제거 (OCR 오류)
    text = re.sub(r'[\u4e00-\u9fff]', '', text)
    
    # 3. 리간처 변환
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
    
    # 4. 다중 공백 정규화
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()
```

**정제 후 AI 처리 가능 항목** (추가 정제 불필요):
- 하이픈 줄바꿈 (`Recht-\nfertigung`)
- 화살표 기호 (`-►`, `->`)
- 경미한 오탈자

### 4.5 Citation 생성 규칙

| 언어 | 포맷 | 예시 |
|:---|:---|:---|
| **de** (판본 포함) | `{abbr}, {ed}. Aufl., Bd. {vol}, {page}` | RGG, 4. Aufl., Bd. IV, 235 |
| **de** (판본 생략) | `{abbr}, Bd. {vol}, {page}` | TRE, Bd. XII, 45 |
| **en** (판본 포함) | `{abbr}, {ed} ed., Vol. {vol}, {page}` | NIDNTT, 2nd ed., Vol. 3, 45 |
| **en** (판본 생략) | `{abbr}, Vol. {vol}, {page}` | TDNT, Vol. III, 42 |
| **monograph** | `{author}, {abbr} {vol}/{part}, {page}` | Barth, KD I/1, 123 |

### 4.6 Themes 태깅 전략

**하이브리드 방식**:
- 문서 메타데이터에 **기본 themes** 설정 (검색 범위)
- 중요 청크에만 **추가 themes** 태깅 (선택)

```json
{
  "metadata": {
    "default_themes": ["조직신학", "Systematic Theology", "Dogmatik"]
  },
  "chunks": [
    {
      "id": "rgg4_0235_001",
      "themes": ["칭의", "Justification", "Rechtfertigung"]  // 추가 태깅
    },
    {
      "id": "rgg4_0236_001",
      "themes": null  // default_themes 상속
    }
  ]
}
```

### 4.7 청킹 프리셋

```yaml
# config/chunking_presets.yaml
presets:
  dictionary_small:
    chunk_size: 2500
    overlap: 500
    examples: [EKL]
  
  dictionary_large:
    chunk_size: 4000
    overlap: 700
    examples: [TRE, RGG, HWPh]
  
  lexicon:
    chunk_size: 3500
    overlap: 600
    examples: [ThWAT, EWNT, TDNT]
  
  monograph:
    chunk_size: 6000
    overlap: 1000
    examples: [KD]
  
  commentary:
    chunk_size: 4000
    overlap: 700
    examples: [BK, EKK]
```

---

## 📐 JSON Schema (Final)

### 문서 메타데이터 (`docs/{doc_id}.meta.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DocumentMetadata",
  "type": "object",
  "required": ["doc_id", "source", "abbr", "title", "language", "doc_type"],
  "properties": {
    "doc_id": { "type": "string", "description": "전역 문서 ID (예: RGG_4_4)" },
    "source": { "type": "string", "description": "원본 파일명" },
    "abbr": { "type": "string" },
    "title": { "type": "string" },
    "volume": { "type": "integer" },
    "edition": { "type": "integer" },
    "part": { "type": "string", "description": "KD의 경우 I/1, I/2 등" },
    "year": { "type": "integer" },
    "language": { "type": "string", "enum": ["de", "en"] },
    "doc_type": { 
      "type": "string",
      "enum": ["dictionary_small", "dictionary_large", "lexicon", "monograph", "commentary"]
    },
    "default_themes": {
      "type": "array",
      "items": { "type": "string" },
      "description": "문서 전체에 적용되는 기본 검색 키워드"
    },
    "page_offset": { "type": "integer" },
    "chunk_size": { "type": "integer" },
    "chunk_overlap": { "type": "integer" },
    "total_chunks": { "type": "integer" },
    "indexed_at": { "type": "string", "format": "date-time" }
  }
}
```

### 청크 (`chunks/{doc_id}.jsonl`, 1 line = 1 chunk)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChunkRecord",
  "type": "object",
  "required": ["global_chunk_id", "doc_id", "chunk_id", "pdf_page", "printed_page", "content", "citation"],
  "properties": {
    "global_chunk_id": { "type": "string", "description": "전역 청크 ID (예: RGG_4_4:0235_001)" },
    "doc_id": { "type": "string" },
    "chunk_id": { "type": "string", "description": "문서 내 로컬 ID (예: 0235_001)" },
    "pdf_page": { "type": "integer", "description": "원본 PDF 페이지 (0-based)" },
    "printed_page": { "type": "integer", "description": "offset 적용 후 인쇄 페이지" },
    "content": { "type": "string", "description": "NFC 정규화된 청크 텍스트" },
    "citation": { "type": "string", "description": "인용 포맷 (예: RGG, 4. Aufl., Bd. IV, 235)" },
    "themes": {
      "type": ["array", "null"],
      "items": { "type": "string" },
      "description": "null = default_themes 상속, [] = 명시적 비움"
    }
  }
}
```

### Manifest (`manifest.json`)

```json
{
  "version": "1.0",
  "updated_at": "2026-01-13T10:00:00",
  "documents": {
    "RGG_4_4": {
      "meta_path": "docs/RGG_4_4.meta.json",
      "chunks_path": "chunks/RGG_4_4.jsonl"
    }
  }
}
```

---

## ✅ Milestones & Checklist

### Phase 1: MCP Server 기본 (Priority: 🔴) ✅ Complete
- [x] 프로젝트 폴더 구조 생성
- [x] `server.py` 스켈레톤
- [x] `searcher.py` 기본 구조
- [x] `models.py` Pydantic 모델
- [x] Antigravity MCP 설정

### Phase 2: search 도구 (Priority: 🔴) ✅ Complete
- [x] `glossary.json` 생성 (3중 언어) - 75개 용어
- [x] `expand_query` 구현 (glossary 연동) - 테스트 완료: 칭의 → [義認, Rechtfertigung, 칭의, Justification]
- [x] `grep_search` 구현 (grep/ripgrep 자동 감지)
- [x] `search` 도구 완성
- [x] `list_sources` 구현

### Phase 3: 파일럿 테스트 (Priority: 🟡) 🔄 Ready
- [ ] EKL 데이터로 검색 테스트 ← **다음 단계**
- [x] `get_chunk` 구현 & 테스트
- [ ] 통합 테스트

### Phase 4: 청킹 파이프라인 (Priority: 🔴) ✅ Complete
- [x] `known_sources.yaml` 생성 - 20+ 소스 정의
- [x] `chunking_presets.yaml` 생성 - 5개 프리셋
- [ ] Pre-Chunking HITL 워크플로우 (Antigravity 대화) ← **문서 처리 시**
- [x] `chunker.py` Main Chunking 스크립트
- [x] Citation 템플릿 로직 (언어별)
- [x] Themes 하이브리드 태깅

### Phase 5: 문서 처리 (Priority: 🟢)
- [ ] EKL 재처리 (새 스키마)
- [ ] RGG 처리
- [ ] TRE 처리
- [ ] KD 처리
- [ ] ThWAT, EWNT 처리
- [ ] BK, EKK 처리

### Phase 6: Translation Pipeline (Modified Phase 6)

> **Goal**: msn_th_db를 신학 번역 워크벤치로 확장. RAG 검색 + 용어 일관성 + 번역 아카이빙.

### 6.0 번역 아키텍처 개요
- [x] **Workflow 정의**: PDF -> OCR -> Chunking (Paragraph) -> Translation (w/ Glossary) -> Archive
- [x] **Translator Module (`translator.py`)**: Glossary Lookup & Archive Manager 구현 완료

### 6.1 Glossary v2.0 스키마
- [x] **Schema Design**: Canonical terms, Alternatives, Definitions
- [x] **Data Migration**: `tre_terms.csv` (3700+ terms) integrated with legacy glossary.

### 6.2 문단 기반 청킹 (Paragraph Chunking)
- [x] **Preset Config**: `strategy: paragraph` in `chunking_presets.yaml`
- [x] **Chunker Logic**: `chunk_by_paragraph` implemented in `chunker.py`
- [x] **Translation Friendly**: Native PDF 처리 시 `_KR.jsonl` (Draft) 자동 생성 로직 추가.

### 6.3 각주 처리 전략
- [x] **Detection**: Conservative regex pattern `[n]`, `(n)`
- [x] **Storage**: `ChunkType.FOOTNOTE` and `parent_chunk_id` supported in models.

### 6.4 MCP Tool Integration (Completed)
- [x] `lookup_term`: Glossary 조회 도구
- [x] `save_translation`: 번역 아카이빙 도구
### 6.4 Agentic Review System (Team Workflow)
단순 번역을 넘어 품질 보증(QA)을 위한 3-Persona 협업 모델을 도입합니다.

1.  **구성원 (Agents)**:
    -   **Draft Translator**: 1차 번역 담당. 직역과 용어 정확성 중심. (Status: `draft`)
    -   **Theological Reviewer**: 신학적 검수 담당. 문맥, 교리적 뉘앙스 비평. (Status: `review`)
    -   **Final Editor**: 최종 확정 담당. 가독성 개선 및 JSONL 반영. (Status: `done`)

2.  **데이터 흐름 (Status Lifecycle)**:
    -   `todo` (미번역) -> `fetch_batch`
    -   `draft` (초벌) -> `submit_draft`
    -   `review` (감수 중) -> 코멘트 추가 (`critique`)
    -   `done` (완료) -> `finalize`

3.  **구현 요구사항 (Next Steps)**:
    -   JSONL 스키마에 `review_comments` 필드 추가.
    -   MCP 도구 확장: `submit_draft`, `submit_review`, `finalize_translation`.

---

## 🔧 Phase 6: Translation Pipeline (PRD)

> **Goal**: msn_th_db를 신학 번역 워크벤치로 확장. RAG 검색 + 용어 일관성 + 번역 아카이빙.

### 6.0 번역 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                    Translation Workflow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [원문 PDF]                                                      │
│       ↓                                                          │
│  [Pre-Chunk] → 문단 경계 감지 + 각주 분리                         │
│       ↓                                                          │
│  [Main Chunk] → 문단 기반 청킹 (본문/각주 분리 저장)              │
│       ↓                                                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ [Antigravity 번역 세션]                                     │ │
│  │                                                             │ │
│  │  1. 청크 로드 (MCP: get_chunk)                              │ │
│  │  2. 용어 조회 (MCP: lookup_term) → glossary v2.0            │ │
│  │  3. 번역 수행 (Antigravity LLM)                             │ │
│  │  4. 번역문 저장 (MCP: save_translation)                     │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│       ↓                                                          │
│  [번역 JSONL] → {doc_id}_KR.jsonl                                │
│       ↓                                                          │
│  [향후 검색 시 원문+번역문 동시 활용]                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.1 Glossary v2.0 스키마

**현재 (v1.0)**: 단순 동의어 목록
```json
"칭의": ["Justification", "Rechtfertigung", "義認"]
```

**확장 (v2.0)**: 다층 번역 용어집

```json
{
  "_meta": {
    "version": "2.0",
    "type": "translation_glossary",
    "updated": "2026-01-13"
  },
  
  "terms": {
    "Rechtfertigung": {
      "id": "term_rechtfertigung",
      "canonical": {
        "ko": "칭의",
        "en": "Justification",
        "de": "Rechtfertigung"
      },
      "alternatives": {
        "ko": ["의롭다 하심", "의인됨", "의화"],
        "en": ["justifying", "to justify", "being justified"],
        "de": ["Rechtfertigungslehre", "gerechtfertigt"]
      },
      "context_rules": [
        {
          "author": "Barth",
          "prefer_ko": "칭의",
          "note": "바르트는 화해론 맥락에서 사용"
        },
        {
          "author": "Luther",
          "prefer_ko": "의롭다 하심",
          "note": "루터 번역 전통에서 선호"
        }
      ],
      "part_of_speech": "noun",
      "domain": ["조직신학", "구원론", "Soteriologie"],
      "related_terms": ["Heiligung", "Sünde", "Gnade", "Glaube"],
      "antonyms": ["Verdammnis", "Verwerfung"],
      "etymology": "recht (right) + fertigen (to make)",
      "notes": "바르트 KD IV/1의 핵심 개념. 화해론(Versöhnungslehre)의 첫 번째 측면."
    }
  },
  
  "persons": {
    "Barth": {
      "id": "person_barth",
      "full_name": {
        "de": "Karl Barth",
        "ko": "카를 바르트"
      },
      "alt_names": {
        "ko": ["칼 바르트", "바르트", "K. 바르트"],
        "en": ["K. Barth", "Karl Barth"]
      },
      "lifespan": "1886-1968",
      "tradition": "Reformed",
      "major_works": ["KD", "Römerbrief"],
      "related_persons": ["Bonhoeffer", "Brunner", "Bultmann"]
    }
  },
  
  "works": {
    "KD": {
      "id": "work_kd",
      "full_title": {
        "de": "Kirchliche Dogmatik",
        "ko": "교회교의학",
        "en": "Church Dogmatics"
      },
      "author": "Barth",
      "volumes": ["I/1", "I/2", "II/1", "II/2", "III/1", "III/2", "III/3", "III/4", "IV/1", "IV/2", "IV/3", "IV/4"],
      "citation_template": {
        "de": "Barth, KD {vol}, {page}",
        "ko": "바르트, 『교회교의학』 {vol}, {page}쪽"
      }
    }
  },
  
  "abbreviations": {
    "vgl.": { "expansion": "vergleiche", "ko": "참조", "en": "compare" },
    "s.": { "expansion": "siehe", "ko": "보라", "en": "see" },
    "u.a.": { "expansion": "unter anderem", "ko": "그 외에", "en": "among others" },
    "z.B.": { "expansion": "zum Beispiel", "ko": "예를 들어", "en": "for example" },
    "d.h.": { "expansion": "das heißt", "ko": "즉", "en": "that is" },
    "a.a.O.": { "expansion": "am angegebenen Ort", "ko": "앞의 책", "en": "loc. cit." },
    "ebd.": { "expansion": "ebenda", "ko": "같은 곳", "en": "ibid." }
  }
}
```

**스키마 필드 설명**:

| 섹션 | 필드 | 설명 |
|:---|:---|:---|
| **terms** | `canonical` | 언어별 표준 번역어 |
| | `alternatives` | 대안 번역어 (검색용) |
| | `context_rules` | 저자/문맥별 선호 번역어 |
| | `domain` | 신학 분야 태그 |
| | `related_terms` | 관련 용어 네트워크 |
| **persons** | `alt_names` | 표기 변형 (검색용) |
| | `major_works` | 주요 저작 (work ID 참조) |
| **works** | `citation_template` | 언어별 인용 포맷 |
| **abbreviations** | — | 독일어 약어 확장 (번역 보조) |

### 6.2 문단 기반 청킹 (Paragraph Chunking)

**기존 방식**: 문자 수 기반 분할 → 문단 중간 절단 위험

**새 방식**: 문단 경계 감지 후 지능형 분할

#### 6.2.1 청킹 프리셋 확장

```yaml
# config/chunking_presets.yaml (추가)
presets:
  # 기존 프리셋 유지...
  
  translation:
    description: "번역용 문단 기반 청킹"
    strategy: paragraph          # NEW
    paragraph_markers:
      primary:
        - pattern: "\\n\\n"      # 빈 줄 (가장 신뢰)
        - pattern: "\\n\\s*\\n"  # 공백 포함 빈 줄
      secondary:
        - pattern: "^\\d+\\."    # 번호 시작 (1. 2. 3.)
        - pattern: "^[A-Z][a-z]" # 대문자 시작 (새 문단 추정)
        - pattern: "^\\s{4,}"    # 들여쓰기 4칸 이상
    constraints:
      max_chars: 6000            # 문단이 너무 길면 분할
      min_chars: 300             # 문단이 너무 짧으면 병합
      preserve_sentence: true    # 문장 중간 절단 금지
    footnote_handling:
      detect_pattern: "\\[\\d+\\]|\\(\\d+\\)|^\\d+\\s"
      separate_storage: true     # 각주 별도 JSONL
```

#### 6.2.2 문단 청킹 알고리즘

```python
def chunk_by_paragraph(text: str, preset: dict) -> List[Chunk]:
    """
    문단 기반 청킹 알고리즘
    
    1. 문단 경계 감지
    2. 각 문단 길이 평가
    3. 너무 짧으면 병합, 너무 길면 문장 경계에서 분할
    4. 각주 분리 (별도 처리)
    """
    paragraphs = detect_paragraphs(text, preset['paragraph_markers'])
    chunks = []
    buffer = ""
    
    for para in paragraphs:
        # 각주 감지 및 분리
        body, footnotes = extract_footnotes(para, preset['footnote_handling'])
        
        # 문단 길이 체크
        if len(buffer) + len(body) < preset['constraints']['min_chars']:
            # 너무 짧음 → 버퍼에 누적
            buffer += "\n\n" + body
        elif len(body) > preset['constraints']['max_chars']:
            # 너무 김 → 문장 경계에서 분할
            if buffer:
                chunks.append(create_chunk(buffer))
                buffer = ""
            sub_chunks = split_at_sentence_boundary(body, preset['constraints']['max_chars'])
            chunks.extend(sub_chunks)
        else:
            # 적정 길이
            if buffer:
                chunks.append(create_chunk(buffer))
                buffer = ""
            chunks.append(create_chunk(body))
        
        # 각주는 별도 저장
        if footnotes:
            for fn in footnotes:
                chunks.append(create_footnote_chunk(fn, parent_id=chunks[-1].id))
    
    return chunks
```

### 6.3 각주 처리 전략

**신학책 각주의 특성**:
- 본문보다 중요한 경우 多 (특히 바르트 KD!)
- 참조 문헌 정보 포함
- 원어 설명, 반론, 보충 논의
- 각주 안에 또 각주 참조 가능

#### 6.3.1 각주 저장 구조

```
msn_th_archive/
├── chunks/
│   ├── KD_1_1.jsonl              # 본문 청크
│   ├── KD_1_1.footnotes.jsonl    # 각주 청크 (분리)
│   ├── KD_1_1_KR.jsonl           # 번역문 (본문)
│   └── KD_1_1_KR.footnotes.jsonl # 번역문 (각주)
```

#### 6.3.2 각주 청크 스키마

```json
{
  "global_chunk_id": "KD_1_1:fn_0123_001",
  "doc_id": "KD_1_1",
  "chunk_type": "footnote",
  "parent_chunk_id": "KD_1_1:0123_001",
  "footnote_number": 1,
  "footnote_marker": "[1]",
  
  "content": "Vgl. Schleiermacher, Der christliche Glaube, §3. Siehe auch Brunner...",
  
  "references_extracted": [
    {
      "type": "citation",
      "author": "Schleiermacher",
      "work": "Der christliche Glaube",
      "location": "§3"
    },
    {
      "type": "cross_reference",
      "author": "Brunner",
      "work": null,
      "location": null
    }
  ],
  
  "pdf_page": 135,
  "printed_page": 123,
  "citation": "Barth, KD I/1, 123, Anm. 1"
}
```

#### 6.3.3 각주 검색 동작

```
[검색 쿼리: "Schleiermacher Glaube"]
          ↓
[MCP: search] → 매칭: KD_1_1:fn_0123_001 (각주)
          ↓
[parent_chunk_id 추적] → KD_1_1:0123_001 (본문)
          ↓
[반환]
{
  "main_chunk": { ... 본문 ... },
  "related_footnotes": [
    { ... 각주 1 ... },
    { ... 각주 2 ... }
  ],
  "context": "본문과 각주 함께 제공"
}
```

### 6.4 번역 MCP 도구

#### 6.4.1 `lookup_term` 도구

```python
@app.tool()
async def lookup_term(
    term: str,
    source_lang: str = "de",
    target_lang: str = "ko",
    context: str = None  # e.g., "Barth", "Luther"
) -> dict:
    """
    glossary v2.0에서 번역어 조회
    
    Returns:
        {
            "term": "Rechtfertigung",
            "canonical": "칭의",
            "alternatives": ["의롭다 하심", "의인됨"],
            "context_match": {
                "author": "Barth",
                "prefer": "칭의",
                "note": "바르트는 화해론 맥락에서 사용"
            },
            "related": ["Heiligung", "Gnade"]
        }
    """
    pass
```

#### 6.4.2 `translate_chunk` 도구 (힌트 제공용)

```python
@app.tool()
async def translate_chunk(
    chunk_id: str,
    target_lang: str = "ko",
    include_glossary_hints: bool = True
) -> dict:
    """
    청크 번역을 위한 컨텍스트 준비
    (실제 번역은 Antigravity LLM이 수행)
    
    Returns:
        {
            "chunk": { ... 원문 청크 ... },
            "footnotes": [ ... 관련 각주 ... ],
            "glossary_hints": [
                {"term": "Rechtfertigung", "translate_as": "칭의"},
                {"term": "Gnade", "translate_as": "은혜"}
            ],
            "previous_chunk_summary": "앞 청크 요약 (문맥용)",
            "citation": "Barth, KD I/1, 123"
        }
    """
    pass
```

#### 6.4.3 `save_translation` 도구

```python
@app.tool()
async def save_translation(
    source_chunk_id: str,
    translated_content: str,
    target_lang: str = "ko",
    translator: str = "과레스키",
    glossary_applied: list = None,
    reviewed: bool = False
) -> dict:
    """
    번역문을 JSONL 아카이브에 저장
    
    Creates: {doc_id}_{lang}.jsonl entry
    """
    pass
```

### 6.5 번역 워크플로우 (Antigravity 세션)

```
[사용자] "KD I/1, 123페이지 번역해줘"
          ↓
[Antigravity]
  1. MCP: get_chunk("KD_1_1:0123_001")
  2. MCP: lookup_term("Rechtfertigung", context="Barth")
  3. MCP: lookup_term("Gnade", context="Barth")
          ↓
[Antigravity: 번역 수행]
  - glossary 힌트 적용
  - 문맥 고려
  - 각주 포함 번역
          ↓
[사용자 검토] ← HITL
          ↓
[Antigravity]
  MCP: save_translation(
    source_chunk_id="KD_1_1:0123_001",
    translated_content="...",
    glossary_applied=["Rechtfertigung→칭의", "Gnade→은혜"]
  )
          ↓
[저장 완료] → msn_th_archive/chunks/KD_1_1_KR.jsonl
```

### 6.6 번역 청크 스키마

```json
{
  "global_chunk_id": "KD_1_1_KR:0123_001",
  "doc_id": "KD_1_1_KR",
  "source_chunk_id": "KD_1_1:0123_001",
  "chunk_type": "body",
  
  "content": "(한국어 번역문)",
  "paragraph_index": 3,
  
  "translation_meta": {
    "source_lang": "de",
    "target_lang": "ko",
    "translator": "과레스키",
    "method": "AI-assisted",
    "reviewed": true,
    "review_date": "2026-01-13",
    "glossary_applied": [
      {"term": "Rechtfertigung", "translated_as": "칭의"},
      {"term": "Gnade", "translated_as": "은혜"}
    ]
  },
  
  "footnote_refs": ["KD_1_1_KR:fn_0123_001"],
  
  "pdf_page": 135,
  "printed_page": 123,
  "citation": "바르트, 『교회교의학』 I/1, 123쪽"
}
```

### 6.7 파일 구조 확장

```
MS_Dev.nosync/
├── projects/
│   └── msn_th_db/
│       ├── src/
│       │   ├── server.py            # MCP Server
│       │   ├── searcher.py          # 검색 로직
│       │   ├── chunker.py           # 청킹 (문단 기반 확장)
│       │   ├── translator.py        # NEW: 번역 도구 로직
│       │   └── models.py            # Pydantic 모델 (확장)
│       ├── config/
│       │   ├── glossary.json        # v2.0으로 마이그레이션
│       │   ├── known_sources.yaml
│       │   └── chunking_presets.yaml # paragraph 전략 추가
│       └── ...
│
└── data/
    └── msn_th_archive/
        ├── docs/
        │   ├── KD_1_1.meta.json
        │   └── KD_1_1_KR.meta.json   # 번역문 메타데이터
        ├── chunks/
        │   ├── KD_1_1.jsonl          # 원문 본문
        │   ├── KD_1_1.footnotes.jsonl # 원문 각주
        │   ├── KD_1_1_KR.jsonl       # 번역 본문
        │   └── KD_1_1_KR.footnotes.jsonl # 번역 각주
        └── manifest.json
```

---

## 📝 Notes

- **레거시**: `Theology_AI_Lab_v4`는 배포용으로 유지
- **실행 환경**: Pre-Chunking=Antigravity, Main Chunking=로컬 Python
- **OCR**: 이미 완료된 PDF 대상
- **Peer Review**: 2026-01-13 반영 (JSONL, global_chunk_id, pdf_page)
- **Phase 6**: 2026-01-13 추가 (Translation Pipeline - glossary v2.0, 문단 청킹, 각주 처리)

---

## 🚀 Quick Start

### MCP 서버 재시작
Antigravity를 재시작하면 `msn_th_db` MCP 서버가 자동 로드됩니다.

### 문서 청킹 (Pre-Chunk → Main Chunk)
1. Antigravity에서 Pre-Chunk 설정 생성 (temp/pre_chunk_config.json)
2. `python src/chunker.py <pdf_path>` 실행

### 번역 워크플로우 (Phase 6)
```bash
# 1. 용어 조회
MCP: lookup_term("Rechtfertigung", context="Barth")

# 2. 청크 로드 + 번역 힌트
MCP: translate_chunk("KD_1_1:0123_001")

# 3. 번역문 저장
MCP: save_translation(
  source_chunk_id="KD_1_1:0123_001",
  translated_content="...",
  translator="과레스키"
)
```

---

*Last Updated: 2026-01-13 15:40 KST*

