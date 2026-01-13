# Gemini Scholar Pipeline v2.0

**Google Gemini Deep Research + Scholar Labs Semantic Search**가 결합된 차세대 신학 연구 자동화 파이프라인입니다.

본 프로젝트는 두 가지 운영 모드를 지원합니다:
1. **Standard Pipeline (`pipeline.sh`)**: 단계별로 명확하게 구분된 6단계 정형 워크플로우 (대규모 리포트용)
2. **Autonomous Writer (`evidence_writer.py`)**: 검색과 저술을 스스로 반복하는 에이전트 모드 (단일 주제 심층 탐구용)

## 🚀 시작하기 (Getting Started)

### Step 0: 모드 선택 가이드 (Select Your Mode)

작업의 목적에 따라 적합한 모드를 선택하세요.

| 상황 | 추천 모드 | 특징 | 명령어 예시 |
| :--- | :---: | :--- | :--- |
| **"이 주제에 대해 A to Z로 쫙 훑어줘."**<br>(광범위한 리포트, 배경 지식 탐색) | **Mode A**<br>(Standard) | • 6단계 정형 프로세스<br>• 웹 레퍼런스와 논문을 모두 수집<br>• 긴 호흡의 종합 리포트 생성 | `./pipeline.sh "주제"` |
| **"이 구체적인 주장에 대해 팩트로 꽉 채운 글 써줘."**<br>(논문 본론 작성, 정밀 타격) | **Mode B**<br>(Autonomous) | • 자율 재귀형 에이전트<br>• 필요한 정보만 핀포인트 검색<br>• 짧고 밀도 높은 학술적 글쓰기 | `python evidence_writer.py "주제"` |

---

### 🕹️ Mode A: Standard Pipeline 사용법

전체 흐름을 한 번에 실행하거나, 각 단계를 끊어서 실행할 수 있습니다.

**1. 일괄 실행 (추천)**
가장 간편한 방법입니다. Phase 1부터 6까지 순차적으로 진행됩니다.

*   **Basic Mode (Standard)**:
    ```bash
    ./pipeline.sh "Moltmann Zimzum" account3
    ```
*   **🔥 Deep Research Mode (Premium)**:
    Gemini Deep Research Agent API를 사용하여 훨씬 더 깊이 있는 분석과 안정적인 논문 검색을 수행합니다.
    ```bash
    ./pipeline.sh --deep "Moltmann Zimzum"
    ```

**2. 단계별 실행 (전문가용)**
중간 결과를 확인하며 진행하고 싶을 때 사용합니다.

*   **Phase 1 (Deep Research)**: 배경 지식 탐색
    ```bash
    ./run_research.sh "Moltmann Zimzum"
    # 결과: reports/Moltmann_Zimzum_raw.md
    ```
*   **Phase 1.5 (Enhancement)**: 심화 및 웹 레퍼런스 DB화
    ```bash
    ./run_depth_enhance.sh account1 "Moltmann Zimzum"
    # 결과: reports/Moltmann_Zimzum_enhanced.md
    ```
*   **Phase 2 (Query Gen)**: 추가 질문 생성
    ```bash
    ./run_query_gen.sh "Moltmann Zimzum"
    # 결과: query.txt
    ```
*   **Phase 3 (Scholar Search)**: 논문 검색 및 DB 적재
    ```bash
    ./run.sh account3 "Moltmann Zimzum"
    # 결과: results/Moltmann_Zimzum.md, scholar_kb.db 업데이트
    ```
*   **Phase 4 (Integration)**: DB 기반 통합 리포트 작성
    ```bash
    ./run_integrate.sh "Moltmann Zimzum"
    # 결과: reports/Moltmann_Zimzum_annotated.md
    ```
*   **Phase 5 (Polish)**: 학술 문체 다듬기
    ```bash
    ./run_polish.sh "Moltmann Zimzum"
    # 결과: reports/Moltmann_Zimzum_final.md
    ```

---

### 🤖 Mode B: Autonomous Writer 사용법

단 하나의 명령어로 검색부터 집필까지 수행합니다.

**1. 기본 실행**
```bash
python evidence_writer.py "Moltmann's concept of Space"
```
*   **작동 방식**:
    1. 내부 DB(`scholar_kb.db`) 조회
    2. 정보 부족 시 구글 스콜라 검색 (Phase 3 기능 자동 호출)
    3. 확보된 Fact로 글 작성
    4. 결과물: `draft_section.md`

**2. 옵션 사항**
`evidence_writer.py` 코드를 열어 `MAX_LOOPS` 등을 조정하여 심도를 조절할 수 있습니다.

---

## 📂 주요 디렉토리 및 파일

| 경로/파일 | 설명 |
|---|---|
| `docs/` | 프로젝트 문서 (README, Architecture 등) |
| `reports/` | 파이프라인 단계별 리포트 출력 (`_raw`, `_annotated`, `_final`, `_report.html`) |
| `results/` | Google Scholar 검색 결과물 (`.md`) |
| `scholar_kb.db` | 수집된 논문과 Fact가 저장되는 Knowledge Base (SQLite) |
| `pipeline.sh` | [Mode A] 전체 파이프라인 관리자 |
| `evidence_writer.py` | [Mode B] 자율 저술 에이전트 |
| `citation_verifier.py` | 인용 무결성 검증 도구 |

---

## ⚠️ 사용자 주의사항

1. **DB 보존**: `scholar_kb.db`는 연구 자산입니다. 삭제하지 않도록 주의하세요.
2. **Environment**: 반드시 `source venv.nosync/bin/activate` 후 실행하세요.
3. **Phase 1.5 (Web Ingestion)**: 리포트의 참고문헌 링크를 DB로 흡수하는 과정은 `web_ingestor.py`를 통해 수동으로 실행 가능합니다.

---
**Version:** 2.1 (Aligning Docs with Execution Steps)
**Last Updated:** 2025-12-12
