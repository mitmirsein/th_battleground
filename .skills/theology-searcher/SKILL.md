---
name: Theology Searcher
description: Search the Theology AI Lab (msn_th_db) JSONL archive using 3-way lexical expansion and grep.
version: 1.0.0
---

# Theology Searcher Skill

## 1. Description
이 스킬은 **Vector DB 없이** 로컬 JSONL 아카이브를 직접 검색합니다. 사용자의 쿼리를 한국어/영어/독일어로 확장한 뒤, `grep`(또는 `rg`)을 사용하여 빠르고 정확하게 문헌을 찾습니다.

## 2. Trigger
- "이 주제로 자료 찾아줘", "바르트 칭의론 검색해줘"
- "#rag", "#검색" 키워드가 입력될 때.

## 3. Workflow Steps

### Phase 1: Query Expansion (쿼리 확장)
1.  **Analyze**: 사용자의 질문에서 핵심 키워드를 추출하십시오.
2.  **Expand**: 키워드를 3개 국어(한/영/독)로 확장하십시오.
    - 예: "성찬" -> `["성찬", "Eucharist", "Abendmahl"]`
    - 이때 `projects/msn_th_db/config/glossary.json`이 있다면 참조하십시오.

### Phase 2: Execution (검색 실행)
1.  **Run**: MCP 도구(`msn_th_db:search`)를 우선적으로 사용하십시오.
    - 만약 MCP가 사용 불가능하다면, 직접 스크립트를 실행하십시오 (아래).
    ```bash
    python projects/msn_th_db/src/server.py --search "쿼리" 
    # 또는 구현된 searcher CLI 사용
    python projects/msn_th_db/utils/cli_search.py "쿼리" 
    ```
2.  **Verify**: 검색 결과가 너무 많으면(50개 이상) 범위를 좁히도록 제안하십시오.

### Phase 3: Synthesis (종합)
1.  **Read**: 검색된 청크(Chunk)들의 내용을 읽으십시오.
2.  **Filter**: LLM의 판단력으로 질문과 관련 없는 청크는 버리십시오. (Semantic Filtering)
3.  **Answer**: 남은 청크들을 인용(`source`)과 함께 종합하여 답변을 작성하십시오.

## 4. Tips
- **속도**: `ripgrep (rg)`이 설치되어 있으면 더 빠릅니다.
- **인용**: 답변 인용 시 반드시 `{abbr}, {volume}, {page}` 형식을 지키십시오.
