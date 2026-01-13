---
name: Scholar Semantic (Google Labs)
description: Performs high-precision semantic search using Google Scholar AI (Labs) agent.
version: 1.0.0
---

# Scholar Semantic Skill

## 1. Description
이 스킬은 **Google Scholar Labs**의 시맨틱 검색 기능을 활용하여 신학 연구 자료를 수집합니다. 단순 키워드 매칭이 아니라, 연구 질문(Research Question)의 의미를 파악하여 관련성이 높은 논문을 찾아줍니다.

## 2. Trigger
- "시맨틱 검색해줘", "구글 스콜라에서 찾아줘", "이 주제 깊게 연구해줘"

## 3. Workflow Steps

### Phase 1: Query Design (질문 설계)
1.  **Understand**: 사용자의 연구 주제와 의도를 파악하십시오.
2.  **Generate Queries**: `Scholar_Architect` 페르소나를 사용하여 **5~10개의 고정밀 연구 질문**을 생성하십시오.
    - **Dual-Language**: 영어(EN)와 독일어(DE)를 섞어서 구성해야 합니다.
    - 예: 
      - "What is the ontological status of justification in Barth?"
      - "Wie verhält sich die Rechtfertigung zur Christologie bei Barth?"
3.  **Save**: 생성된 질문들을 `projects/gemini-scholar-pipeline/temp_queries.txt`에 저장하십시오. (각 줄에 질문 하나씩)

### Phase 2: Execution (실행)
1.  **Run Agent**: 다음 명령어로 `scholar_labs_agent.py`를 실행하십시오.
    ```bash
    cd projects/gemini-scholar-pipeline
    ../../shared_venv/bin/python scholar_labs_agent.py temp_queries.txt --job "{주제_키워드}"
    ```
    *(주의: `--job` 인자는 파일명에 쓰일 식별자입니다. 공백 없이 영어/숫자로 하세요.)*

### Phase 3: Reporting (보고)
1.  **Check Output**: `results/` 폴더에 생성된 마크다운 파일을 확인하십시오.
2.  **Synthesize**: 검색된 논문들의 요약과 주요 인용(Citation)을 정리하여 사용자에게 보고하십시오.

## 4. Tips
- **속도 제한**: 구글 스콜라의 차단(Block)을 피하기 위해 에이전트가 알아서 천천히 작동합니다. 재촉하지 마십시오.
- **로그인**: 만약 실행 중 로그인 오류가 발생하면 사용자에게 "브라우저 로그인이 풀린 것 같습니다"라고 알리십시오.
