---
name: Dictionary Editor
description: Generates standardized theological dictionary articles/wiki entries.
version: 1.0.0
---

# Dictionary Editor Skill

## 1. Description
이 스킬은 신학 용어에 대한 **백과사전식 아티클(Dictionary Entry)**을 작성합니다. 학술적 정확성을 유지하면서도, 웹 게시를 위한 구조화된 포맷(Markdown + Frontmatter)을 준수합니다.

## 2. Trigger
- "사전 아티클 작성해줘", "위키 항목 만들어줘", "OOO에 대한 정의 써줘"

## 3. Workflow Steps

### Phase 1: Preparation (준비)
1.  **Check Term**: 작성할 용어가 `projects/web/theology_article/data/terms.json`에 있는지 확인하고, 다국어 표기(lemma)를 확보하십시오.
2.  **Load Template**: `projects/web/theology_article/templates/article_template.md`를 읽어 기본 구조를 파악하십시오.

### Phase 2: Research & Drafting (연구 및 작성)
1.  **Analyze**: 제공된 RAG 자료나 검색 결과를 분석하십시오.
2.  **Draft**: 다음 표준 목차에 따라 서술하십시오.
    - **정의 (Definition)**: 간결하고 명확한 신학적 정의.
    - **역사 (History)**: 개념의 성서적/교회사적 발전 과정.
    - **전통별 차이 (Confessional Differences)**: 가톨릭, 개신교(루터/개혁), 현대 신학의 관점 차이.
    - **주요 논쟁 (Key Debates)**: 관련된 신학적 쟁점.
    - **1차 근거 (Primary Sources)**: 성경, 공의회 문헌, 주요 신조 인용 (필수).

### Phase 3: Formatting (서식)
1.  **Frontmatter**: `de_lemma`, `en_lemma`, `la_lemma`, `synonyms_ko` 등을 완성하여 문서 상단에 배치하십시오.
2.  **Wiki Links**: 본문 내에서 다른 신학 용어가 나오면 `[[용어]]` 형태로 링크를 거십시오. (SSOT `terms.json` 기준)
3.  **Save**: 결과물을 `projects/web/theology_article/staging/{주제}.md`에 저장하십시오.

## 4. Rules
- **중립성**: 특정 교파의 입장에 치우치지 말고, 객관적으로 기술하십시오.
- **근거 중심**: 모든 주장은 1차 문헌이나 권위 있는 2차 문헌에 근거해야 합니다.
