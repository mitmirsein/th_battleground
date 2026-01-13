---
name: Theology Translator
description: Translates theological documents (JSONL archive) using a 3-stage agentic review process and specialized glossary.
version: 1.0.0
---

# Theology Translator Skill

## 1. Description
이 스킬은 `msn_th_db` 아카이브에 저장된 청크(`chunks/`)를 가져와 **고품질 신학 번역**을 수행합니다. 번역 초안 생성부터 전문가(Agent) 리뷰, 윤문까지 포함합니다.

## 2. Trigger
- "이 문서 번역해줘", "RGG 4권 번역 시작해", "번역 초안 만들어줘"

## 3. Workflow Steps

### Phase 1: Draft Creation (초안 생성)
*청킹은 이미 완료되어 있어야 합니다.*
1.  **Check**: `data/msn_th_archive/translations/{doc_id}_KR.jsonl` 파일이 있는지 확인하십시오.
2.  **Create**: 없다면 `chunks/{doc_id}.jsonl`을 읽어 번역용 파일(Draft)을 생성하십시오.
    - 구조: `{"original": "...", "translation": "(번역 대기)", "status": "todo"}`
    - 팁: 이 단계에서 시스템 스크립트(`create_draft.py` 등)를 사용할 수 있습니다.

### Phase 2: Translation (번역 수행)
1.  **Lookup**: 번역할 텍스트에서 주요 신학 용어(독일어/영어)를 추출하여 `glossary.csv`, `tre_journal.csv`에서 검색하십시오.
2.  **Translate**: 용어집 정의를 준수하여 초벌 번역을 수행하십시오.
    - **Draft Translator Mode**: 직역 위주로 정확하게 번역.

### Phase 3: Theological Review (검수)
1.  **Review**: 초벌 번역문을 '신학자(Theologian)' 페르소나로 검토하십시오.
    - 오역 체크, 신학적 뉘앙스 교정.
    - 문맥에 맞지 않는 용어 수정.

### Phase 4: Final Polish (윤문)
1.  **Polish**: 최종 '편집자(Editor)' 페르소나로 문장을 다듬으십시오.
    - 한국어의 자연스러움, 학술적 품격 유지.
2.  **Save**: 최종 결과물을 `_KR.jsonl`의 `translation` 필드에 저장하고 `status`를 `done`으로 변경하십시오.

## 4. Rules
- **용어 일관성**: 반드시 `projects/msn_th_db/config/glossary.json`의 용어를 최우선으로 따르십시오.
- **각주 처리**: 각주는 본문과 분리하여 번역하되, 본문의 흐름을 끊지 않도록 주의하십시오.
