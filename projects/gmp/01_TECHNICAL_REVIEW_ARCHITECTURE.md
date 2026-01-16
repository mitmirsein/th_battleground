# GMP AI 에이전트 아키텍처: 벡터 DB 없는(Vector-less) 접근 방식

**작성일:** 2026-01-16
**주제:** GMP/제약 규제 대응 에이전트를 위한 벡터 DB 대 파일 기반 인제스천(File-based Ingestion) 기술 타당성 검토
**검토자:** Smilzo (Tech Lead)

## 📋 요약 (Executive Summary)
**결론:** 벡터 DB(Vector DB)는 필수 사항이 아닙니다.
오히려 데이터 무결성(Data Integrity)과 정확한 감사(Audit)가 요구되는 규제 산업(제약/바이오/GMP)에서는, **"청킹 파일 시스템 + 정밀 키워드 검색(Grep)"** 아키텍처가 일반적인 벡터 기반 RAG보다 기술적 적합성이 높습니다.

## ⚖️ 기술 비교 (Comparative Analysis)

| 비교 항목 | 벡터 DB (Semantic Search) | 파일 기반 시스템 + Grep (제안 방식) |
| :--- | :--- | :--- |
| **검색 원리** | 벡터 공간 내 의미적 유사성 (Vibe) | **정확한 키워드 및 코드 매칭 (Exact Match)** |
| **결과 특성** | 확률적 ("비슷한 내용") | **결정론적 ("정확한 문서 번호/조항")** |
| **데이터 무결성** | 블랙박스 (임베딩 값 검증 불가) | **사람이 읽고 검증 가능 (Auditable)** |
| **인프라** | 별도 DB 관리 필요 (유지보수 비용 ↑) | **인프라 불필요 (단순 폴더 관리)** |

## 🏗️ 제안 아키텍처 (Generalized Architecture)

### 1. 데이터 인제스천 (SOP 및 규정)
- **프로세스:** PDF/Word 등 원본 문서에서 텍스트 추출 → 정제 → **구조화된 JSONL 파일**로 변환.
- **메타데이터:** 문서 번호(Document ID), 개정 일자, 페이지 번호 등을 엄격하게 태깅하여 저장. 이는 추후 Audit Trail(감사 추적)을 위해 필수적입니다.
- **저장 방식:** 변환된 텍스트 파일들을 `chunks/`와 같은 폴더 구조에 단순 저장.

### 2. 검색 및 조회 (Search & Retrieval)
- **1단계 (Retrieval):** `grep`이나 `ripgrep`과 같은 도구를 사용하여, 특정 문서 코드(예: "SOP-QA-001", "일탈")를 **결정론적(Deterministic)**으로 찾아냅니다. 놓치는 문서가 없어야 합니다.
- **2단계 (Re-ranking):** 1차로 검색된 약 50여 개의 후보 텍스트를 LLM에게 전달하여, 현재 질문의 문맥에 가장 적합한 내용을 선별하게 합니다. (의미적 판단은 DB가 아닌 LLM이 수행)

### 3. 생성 및 근거 (Generation & Reference)
- **답변 생성:** 오직 검색되고 검증된 청크 내용에 기반해서만 답변을 생성하도록 제한합니다.
- **인용 (Citation):** GMP 밸리데이션 요건을 충족하기 위해, 답변에는 반드시 정확한 출처(예: `[근거: SOP-QA-001, 4페이지]`)가 명시되어야 합니다.

## 🔐 규정 준수 및 밸리데이션 (Compliance & Validation)
- **핵심 과제:** 데이터 무결성(Data Integrity) 및 컴퓨터 시스템 밸리데이션(CSV).
- **해결 방안:**
    - 데이터베이스 자체를 **사람이 읽을 수 있는 텍스트(JSONL)** 형태로 유지함으로써, 검색된 근거가 원본과 일치하는지 언제든 사람이 육안으로 대조 및 검증 가능합니다.
    - 확률에 의존하는 벡터 인덱싱(Black-box)보다, 명확한 규칙 기반의 검색 알고리즘(White-box)이 시스템 밸리데이션(CSV) 대응에 훨씬 유리합니다.

## 🔌 MCP(Model Context Protocol) 통합 아키텍처

### 개요: 검색 엔진과 LLM의 역할 분리
현재 시뮬레이션 스크립트는 "검색"과 "응답 생성"이 하나의 코드에 통합되어 있습니다. 이를 **MCP 프로토콜**을 통해 분리하면, 진정한 생성형 AI(Antigravity/Gemini 등)와의 연동이 가능해집니다.

```
[현재 구조: Standalone Script]
User Query → Python Script (검색 + 응답 생성) → Output

[MCP 통합 구조: Tool + LLM 분리]
User Query → LLM (판단/생성) ←→ MCP Tool (검색/조회) → Output
```

### 역할 분담 원칙

| 구성 요소 | 역할 | 특성 |
|:---|:---|:---|
| **MCP Server (도구)** | 데이터 검색, 문서 조회 | 결정론적, 빠름, 검증 가능 |
| **LLM (두뇌)** | 맥락 판단, 답변 생성, 종합 | 유연함, 자연어, 창의적 |

### MCP Tool 설계 (안)

GMP 에이전트용 MCP Server가 제공할 도구(Tool) 목록:

| Tool 이름 | 기능 | 입력 예시 | 출력 |
|:---|:---|:---|:---|
| `search` | 규정/SOP/이력 통합 검색 | `query="점착력", market="KR"` | 매칭된 청크 리스트 |
| `get_chunk` | 특정 문서 전문 조회 | `doc_id="SOP-QA-001"` | 해당 문서 전체 내용 |
| `list_sources` | 사용 가능한 문서 목록 | `market="US"` | 메타데이터 리스트 |
| `generate_capa` | CAPA 보고서 초안 생성 | `deviation_id="DEV-230205"` | 마크다운 보고서 |

### MCP Server 스켈레톤 코드

```python
# gmp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("gmp_agent")

@app.tool()
async def search(query: str, market: str = "KR", doc_type: str = "all") -> list:
    """
    GMP 규정 및 SOP 검색.
    - query: 검색 키워드
    - market: KR(식약처) 또는 US(FDA)
    - doc_type: sop, regulation, history, all
    """
    results = _grep_search(query, market, doc_type)
    return results

@app.tool()
async def get_chunk(doc_id: str) -> dict:
    """특정 문서의 전체 내용 반환"""
    return _load_document(doc_id)

@app.tool()
async def list_sources(market: str = "all") -> list:
    """사용 가능한 문서 목록 조회"""
    return _get_manifest(market)
```

### Antigravity 설정 (settings.json)

```json
{
  "mcpServers": {
    "gmp_agent": {
      "command": "python",
      "args": ["/path/to/gmp/src/gmp_server.py"],
      "env": {}
    }
  }
}
```

### 통합 후 동작 흐름

```
[사용자 질문]
"점착력 저하 발생. 대응 방안은?"
        ↓
[LLM 내부 사고 과정]
1. "점착력 관련 규정을 찾아야겠다."
2. → gmp_agent:search(query="점착력", doc_type="sop") 호출
3. 결과: SOP-QA-001, SOP-MF-012 반환
4. "과거 유사 사례도 찾아보자."
5. → gmp_agent:search(query="점착력 저하", doc_type="history") 호출
6. 결과: DEV-230205 반환
7. "이제 종합해서 답변을 만들자."
        ↓
[LLM 최종 답변 생성]
"점착력 저하 현상에 대해 다음과 같이 대응하시기 바랍니다:
1. SOP-QA-001 제4.2.3항에 따라 즉시 격리 조치...
2. SOP-MF-012에 따라 건조기 온도 점검...
3. 과거 사례(DEV-230205) 참조: 히터 고장 가능성..."
```

### MCP 통합의 이점

1. **유연한 응답 생성**: 하드코딩된 템플릿이 아닌, LLM이 실시간으로 맥락에 맞는 답변 생성.
2. **무한 확장성**: 새로운 유형의 질문에도 코드 수정 없이 대응 가능.
3. **정확한 인용**: LLM이 검색 결과를 기반으로 근거를 자동 인용.
4. **역할 분리**: 검색(도구)과 판단(LLM)이 각자의 영역에서 최적 성능 발휘.
