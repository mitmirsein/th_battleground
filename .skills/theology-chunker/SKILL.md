---
name: Theology Chunker
description: Ingests PDF/Text documents into the msn_th_db JSONL archive using the specialized chunker.
version: 1.0.0
---

# Theology Chunker Skill

## 1. Description
이 스킬은 PDF 문서를 **Theology AI Lab (msn_th_db)**의 아카이브 포맷(JSONL)으로 변환하는 시작점입니다. PDF의 텍스트를 추출, 정제하고 의미 단위(문단 등)로 쪼개어 저장합니다.

## 2. Trigger
- "이 PDF 청킹해줘", "자료 DB에 넣어줘", "아카이빙해줘"
- `/arc` 명령어와 함께 PDF가 주어졌을 때.

## 3. Workflow Steps

### Phase 1: Configuration (설정)
1.  **Analyze**: 대상 PDF 파일명을 분석하여 `known_sources.yaml`에 있는 문서인지 확인하십시오.
    - 예: `RGG_Vol4.pdf` -> `abbr: RGG`, `volume: 4`
2.  **Ask**: 필수 메타데이터가 부족하면 사용자에게 물어보십시오.
    - 특히 **`page_offset`** (PDF 페이지 - 실제 인쇄 페이지 차이)은 반드시 확인해야 합니다.
    - "이 책의 실제 인쇄 페이지가 PDF 페이지와 얼마나 차이나나요?"
3.  **Generate Config**: 수집된 정보를 바탕으로 `temp/pre_chunk_config.json` 파일을 생성하십시오.
    - `strategy`: 번역이 목적이라면 `"paragraph"`를 권장하십시오.

### Phase 2: Execution (실행)
1.  **Run**: `projects/msn_th_db/src/chunker.py`를 실행하십시오.
    ```bash
    python projects/msn_th_db/src/chunker.py "/path/to/file.pdf" --config projects/msn_th_db/temp/pre_chunk_config.json
    ```
2.  **Verify**: 실행 결과(`✅ Done!`)를 확인하고, 생성된 Chunk 수와 저장 위치를 사용자에게 보고하십시오.

## 4. Tips
- **OCR Quality**: OCR이 안 된 파일은 처리할 수 없습니다. OCR 여부를 먼저 체크하세요.
- **Constraints**: 문단 청킹 시 `min_chars: 300`, `max_chars: 6000` 정도가 적당합니다.
