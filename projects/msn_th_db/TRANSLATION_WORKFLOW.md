---
share_url: https://jsp.ellpeck.de#6d8648ba
---


# 🏛️ MSN Theology Translation Pipeline Guide

> **Version**: 1.0 
> **System**: Antigravity RAG + MCP Server  
> **Goal**: 신학 원서의 고품질 한글 번역 및 아카이빙

---

## 🏗️ Architecture Overview

이 파이프라인은 PDF 원문을 **문단 단위(Paragraph)**로 분해하고, **신학 용어집(Glossary, TRE Lemma 3700여 개 통합)**을 참조하여 AI가 번역한 뒤, **JSONL** 형식으로 영구 보존하는 시스템입니다.

```mermaid
graph LR
    PDF[PDF 원문] -->|ocr_tool.py| TXT[OCR Text]
    TXT -->|init_translation.py| JSONL[Translation Archive (_KR.jsonl)]
    JSONL -->|fetch_batch| MCP[MCP Server]
    MCP -->|Context| AI[Antigravity (LLM)]
    AI -->|Translation| MCP
    MCP -->|submit_batch| JSONL
```

---

## 🛠️ Core Components

### 1. Extraction Strategy (Hybrid)
- **Native PDF**: `PyMuPDF`를 사용하여 텍스트 라인과 좌표를 정밀하게 추출합니다.
- **Scanned PDF**: 이미지 렌더링 후 `Tesseract` OCR을 사용하여 텍스트를 인식합니다.
- **특징**: 독일어/영어/그리스어/히브리어 다중 언어 지원.
- **사용법**:
  ```bash
  python src/ocr_tool.py <input.pdf> <output.txt> [max_pages]
  ```

### 2. Paragraph Chunker (`src/chunker.py`)
텍스트를 문맥 유지를 위해 **문단 단위**로 자릅니다.
- **전략**: `strategy: paragraph`
- **기능**: 각주(`[n]`, `(n)`)를 자동 감지하여 별도 메타데이터로 관리.
    > *Note: OCR에서 위첨자가 일반 숫자(`text1`)로 변환된 경우, Draft Translator(AI)가 문맥을 파악하여 `[n]` 형식으로 복원합니다.*
- **설정**: `config/chunking_presets.yaml`에서 `translation` 프리셋 사용.

### 3. Translator Module (`src/translator.py`)
번역 데이터와 용어집을 관리하는 핵심 모듈입니다.
- **Glossary Manager**: 
    - `config/glossary.json` (v2.0, **TRE Lemma 기반 3700+ 용어 통합**)
    - `data/tre_journal.csv` (**저널 약어 700+ 통합**)
- **Translation Archive**: `data/msn_th_archive/translations/` 디렉토리에 저장.
- **Batch Processing**: `get_next_batch` / `save_batch` 지원.

### 4. MCP Server Tools (`src/server.py`)
Antigravity가 번역 작업을 수행할 수 있도록 도구를 제공합니다.
- `lookup_term(query)`: 용어 조회.
- `fetch_translation_batch(doc_id, size)`: 번역 대기 중인 청크 가져오기.
- `submit_translation_batch(doc_id, translations)`: 번역 결과 일괄 저장.
- `save_translation`: 단일 번역 저장.

---

## 📂 Data Structure

### 1. Glossary v2.0 & Journal DB
용어와 저널 약어를 통합 관리합니다.

**Glossary (`config/glossary.json`)**:
```json
"Analogie": {
  "id": "term_analogie",
  "canonical": { "de": "Analogie", "ko": "유비" },
  "definitions": { "ko": "..." }
}
```

**Journal DB (`data/tre_journal.csv`)**:
```csv
AA,Archäologischer Anzeiger,고고학 연보,...
ZNW,Zeitschrift für die neutestamentliche Wissenschaft,신약학 저널...
```
*`lookup_term("ZNW")` 호출 시 저널 정보가 함께 반환됩니다.*

### 2. Translation Archive (`*_KR.jsonl`)
모든 번역 작업의 상태를 추적하는 마스터 파일입니다.
```json
{
  "chunk_id": "0625_001",
  "original": "Analogie ...",
  "translation": "(번역 대기)..." OR "유비는...",
  "metadata": {
    "status": "todo" | "done",
    "chunk_type": "body"
  }
}
```

---

## 🚀 Workflow Guide

### Step 1: 프로젝트 초기화 (청킹 & 번역 파일 생성)

문서 유형에 따라 두 가지 방법이 있습니다.

**Case A: 텍스트 PDF (Native Type)**
텍스트 복사가 가능한 PDF는 `chunker.py`를 통해 한 번에 처리합니다.
```bash
python src/chunker.py input.pdf --strategy translation --id DOC_ID
```
> 결과: `chunks/` 및 `translations/` 파일 동시 생성.

**Case B: 이미지 PDF (Scanned Type)**
OCR 처리가 필요한 경우 2단계로 진행합니다.
```bash
# 1. OCR 텍스트 추출
python src/ocr_tool.py path/to/doc.pdf temp/doc_ocr.txt

# 2. 번역 프로젝트 생성 (init_translation.py 수정 후 실행)
python src/init_translation.py
```

### Step 2: 반자동 번역 실행 (With Antigravity)
에이전트에게 명령하여 번역을 시작합니다.
1. **명령**: "DOC_ID 문서 번역 작업을 시작해줘." (또는 "검수 팀 모드로 시작해")
2. **진행**: Antigravity가 `fetch_batch` -> 번역/검수 -> `submit_batch` 반복 수행.

---

## 👥 Agentic Team Workflow (검수 프로세스)

고품질 번역을 위해 **3단계 협업 모델**을 따릅니다.

### 1. The Team (Roles)
| Role | Persona Goal | Output Status |
| :--- | :--- | :--- |
| **Draft Translator** | 직역 중심의 정확성, 용어 일관성 준수. | `draft` |
| **Theological Reviewer** | 신학적 문맥, 교리적 뉘앙스, 가독성 검토. | `review` |
| **Final Editor** | 최종 윤문, JSONL 반영. | `done` |

### 2. Interaction Protocol
1. **User**: "Analogie 문서 검수 팀 모드로 시작해."
2. **Draft Translator**: `fetch_batch`로 할 일 수령 -> 번역 -> `submit_draft`.
3. **Theological Reviewer**: Draft 확인 -> 비평(Critique) -> `submit_review`.
4. **Final Editor**: 비평 반영 -> 최종 수정 -> `finalize`.

---

## 📝 Maintenance

- **용어 수정**: `config/glossary.json`을 직접 수정하고 시스템을 재시작하면 즉시 반영됩니다.
- **재번역**: JSONL 파일에서 해당 청크의 `status`를 `"todo"`로 바꾸거나, 그냥 덮어쓰기 번역을 요청하면 이력이 남습니다.
