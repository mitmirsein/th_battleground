# 디지털 코퍼스 구축 표준 가이드라인 v7.0 (The Runbook)

## Phase 1: 지능형 설계 파트너십 (Intelligent Design Partnership)

> **목표:** 문헌의 표면적/내재적 특성을 완벽히 분석하고, 잠재적 리스크를 예측하며, 인간 전문가의 암묵지를 이끌어내는 대화형 설계를 통해, 프로젝트의 성공을 보장하는 '살아있는 설계도(Living Blueprint)'를 공동으로 저술한다.
>
> **주요 수행자:** **인간 아키텍트 (Human Architect)**, **LLM - 설계 파트너 (LLM Design Partner)**

1.  **심층 문헌 프로파일링 (Deep Document Profiling)**
    *   **LLM**은 입력된 PDF와 서지 정보를 바탕으로 **학술적 컨텍스트, 자동 특징 공학, 잠재적 리스크 식별**이 포함된 360° 분석 보고서를 생성한다. 보고서에는 **"표본 CER 측정 방법"을 명시한다. (예: 3개 페이지를 랜덤 추출하여 수작업 정답 대비 CER 계산)**

2.  **소크라테스식 설계 대화 (Socratic Design Dialogue)**
    *   **LLM**은 분석 보고서를 기반으로 **가설 기반 질문**과 **트레이드오프 분석**을 제시하여, 인간 아키텍트와의 대화를 통해 최적의 설계 방향(각주 시스템, 페이지 번호 체계, 구분선 규칙 등)을 함께 결정한다.

3.  **참조 지식 생성 및 표준 준수**
    *   **LLM**은 `sigla_draft.md` (비평 장치 딕셔너리 초안)을 생성하며, **인간**은 이를 검토/보완하여 최종 `sigla.md`를 확정한다. **(권장) 이 파일은 TEI 표준을 참고하여 XML/CSV 형식으로도 병행 저장한다.**
    *   **인간**은 책의 정오표(`Nachträge...`)를 보고 `errata_draft.txt` (인간용 정오표 초안)를 작성한다.
    *   **LLM**은 책의 목차(`Inhaltsverzeichnis`)를 구조화하여 `toc.json`을 생성한다.

4.  **라이브 프로토타이핑 및 동적 튜닝 (Live Prototyping & Dynamic Tuning)**
    *   **LLM**과 **인간**은 대화 과정에서 제안된 **각각의 '프로세서'(파싱 전략 프롬프트)**를 즉시 샘플 데이터로 테스트하고, 그 결과를 실시간으로 피드백하여 프롬프트의 성능을 검증하고 최적화한다.

5.  **'프로젝트 헌장' 최종 생성 (Project Charter Generation)**
    *   모든 논의와 테스트 결과를 종합하여, **LLM**은 다음의 최종 산출물을 생성하고 **인간**이 승인한다.
        *   `project_context.json`: 프로젝트의 철학, 리스크 관리 계획, **`tei_header_path` 같은 표준 메타데이터 참조**가 담긴 헌장.
        *   `parsing_strategy.json`: **LLM의 `model_identifier`와 `tokenizer_version`을 명시하여 재현성을 확보한, '프로세서' 역할의 프롬프트 모음집.**
        *   `schema/schema.py`: **`pydantic` 모델로 코드화된, 최종 데이터의 명확한 스키마 정의.**

---

## Phase 2: 베이스-레이어 구축 (Base-Layer Construction)

> **목표:** 검증된 전문 도구들을 활용한 하이브리드 파이프라인을 통해 원본 문서의 레이아웃과 텍스트를 정확하게 추출하고, LLM을 통해 초기 구조화 태깅을 완료하여 '베이스-레이어'를 생성한다.
>
> **주요 수행자:** **자동화된 하이브리드 파이프라인 (PyMuPDF → OpenCV → Tesseract → LayoutParser → LLM)**, **인간 아키텍트 - 검수자**

1.  **하이브리드 파이프라인 실행 (Hybrid Pipeline Execution)**
    *   **자동화된 스크립트**가 **'다층 오류 탐지 시스템'**을 내장한 채 다음 단계를 순차적으로 실행한다.
        1.  **이미지 추출 및 전처리 (OpenCV):** 스크립트에 **기본 파라미터(DPI ≥ 400, Otsu Threshold 등)를 주석으로 명시하여** 일관성을 유지한다.
        2.  **고급 OCR (Pytesseract):** 특수 폰트(예: Fraktur)에 훈련된 모델을 사용하여 텍스트, 위치, 단어별 신뢰도 점수를 추출한다.
        3.  **레이아웃 분석 (Layout-Parser):** OCR 결과 후처리 시, **"블록의 높이, 평균 폰트 크기, 줄 간격"** 등을 기반으로 한 규칙을 적용하여 오분류를 최소화한다.
        4.  **LLM 태깅 및 구조화:** LLM이 태깅에 실패할 경우, **`{tag: "unclassified", ...}` 형태로 데이터를 남겨** 후처리를 용이하게 한다.

2.  **베이스-레이어 통합 검수 (Base-Layer Unified Review)**
    *   파이프라인 실행 후, **자동으로 생성된 트리아지 보고서**(`검토 필요 페이지 목록`)를 바탕으로 인간 아키텍트가 검수를 진행한다.
    *   **스마트 검수 인터페이스**는 보고서에 언급된 페이지를 열고, 오류 플래그가 붙은 텍스트 블록을 자동으로 하이라이트하여 효율적인 검수를 돕는다.

3.  **베이스-레이어 파일 생성 (Base-Layer File Generation)**
    *   검수가 완료된, 정오표가 적용되지 않은 원본 그대로의 코퍼스가 **`base.json`** 파일로 최종 저장된다.

---

## Phase 3: 강화 및 패치-레이어 구축 (Enrichment & Patch-Layer Construction)

> **목표:** 베이스-레이어에 저자의 최종 의도와 숨겨진 지적 구조를 주입하여, 원본을 뛰어넘는 가치를 가진 최종 코퍼스를 완성한다.
>
> **주요 수행자:** **LLM - 데이터 강화 전문가**, **자동화된 스크립트**, **인간 아키텍트 - 최종 검수자**

1.  **기계용 에라타 생성 (Machine-Readable Errata Generation)**
    *   `errata.json` 생성 시, 각 수정 사항에 **`"edit_type": "insertion" | "deletion" | "substitution"` 필드를 포함**한다.
    *   **LLM**은 `errata_draft.txt`와 `base.json`을 입력받아, **"텍스트 윈도우 유사도와 Levenshtein 거리(`rapidfuzz` 활용)"**를 병행하여 수정 위치를 정확히 찾아낸다.

2.  **목차 메타데이터 주입 (Table of Contents Metadata Injection)**
    *   `inferred_heading` 메타데이터 주입 시, **`"level": 1 | 2 | 3` 과 같이 제목의 계층 정보도 함께 할당**한다.
    *   **LLM**은 **`sentence-transformers`**를 사용하여 목차 항목의 정확한 위치를 찾아낸다.

3.  **자동 패치 적용 및 최종 산출물 생성 (Automated Patching & Finalization)**
    *   **자동화된 스크립트**가 `base.json`에 `errata.json`을 적용하여, 최종 코퍼스인 **`corrected.json`** 파일을 생성한다.
    *   **인간 아키텍트**는 주요 변경 사항 몇 가지를 최종 확인한다.

---

## Phase 4: 품질 보증 및 패키징 (Quality Assurance & Packaging)

> **목표:** 데이터의 무결성을 최종 검증하고, 표준화된 형식으로 코퍼스를 패키징하여 배포 및 재현성을 보장한다.
>
> **주요 수행자:** **자동화된 스크립트**, **인간 아키텍트 - 최종 검토자**

1.  **자동 검증 (Automated Validation)**
    *   **`pydantic` 모델을 사용한 자동 스키마 검증 스크립트**를 **`pytest` 프레임워크와 통합하여** 실행한다.

2.  **버전 관리 및 변경 기록 작성 (Versioning & Changelog)**
    *   **Conventional Commits 규칙**에 따라 `CHANGELOG.md`를 작성하고, `git tag`로 시맨틱 버전을 기록한다.

3.  **최종 패키징 (Final Packaging)**
    *   **`LICENSE` 파일에 `Creative Commons BY-NC 4.0`과 같은 라이선스를 명시**한다.
    *   **(선택) Zenodo에 업로드하여 학술 인용을 위한 DOI를 발급받는다.**

---

## Phase 5: 운영, 유지보수 및 CI/CD (Operations, Maintenance & CI/CD)

> **목표:** 프로젝트의 안정적인 실행, 재현성, 지속 가능성을 보장한다. 문제가 발생했을 때 신속하게 추적하고, 반복 작업을 자동화하며, 미래의 확장을 대비한다.
>
> **주요 수행자:** **자동화된 시스템 (CI/CD, Scripts)**, **인간 아키텍트 - 운영자**

1.  **실행 환경 관리 (Runtime & Dependency Management)**
    *   **런타임 고정:** `python:3.11-slim` 등 특정 버전의 Docker 이미지를 사용하거나, `pyenv`를 통해 Python 버전을 고정한다.
    *   **의존성 잠금:** `pip freeze > requirements.lock` 또는 `poetry.lock` 파일을 생성하여, 모든 라이브러리의 버전을 정확히 고정시킨다.

2.  **보안 및 비밀 관리 (Security & Secret Management)**
    *   `.env` 파일에 API 키를 보관하고, `.gitignore`에 추가한다. `.env.example` 템플릿을 제공한다.
    *   **`pre-commit` 훅**을 사용하여 API 키가 실수로 Git에 커밋되는 것을 원천 차단한다.

3.  **로깅 및 오류 추적 (Logging & Error Tracking)**
    *   **`loguru` 라이브러리**를 도입하여, 모든 실행 기록을 `logs/pipeline_{date}.log` 파일에 남긴다.
    *   `WARNING` 이상의 로그는 콘솔에도 출력한다. 치명적 오류 발생 시, 처리 중이던 데이터를 `interim/FAILED_{timestamp}`와 같은 파일로 덤프하여 유실을 막는다.

4.  **견고성 및 재시도 정책 (Robustness & Retry Policy)**
    *   **LLM API 호출:** 네트워크 오류 시, 지수 백오프(`Exponential Backoff`) 전략으로 최대 3회 자동 재시도한다.
    *   **파이프라인 단계:** 페이지 단위로 `try...except` 블록을 적용하여, 특정 페이지 처리 실패 시 전체 파이프라인이 중단되지 않도록 한다. 실패한 페이지 목록은 별도 파일로 기록한다.

5.  **성능 최적화 (Performance Optimization)**
    *   **병렬 처리:** OCR, 이미지 처리 등 CPU 집약적 작업은 `multiprocessing.Pool`을 사용하여 병렬화한다.
    *   **GPU 자동 감지:** `torch.cuda.is_available()` 또는 `torch.backends.mps.is_available()`를 통해 사용 가능한 GPU를 자동 감지하고 활용한다.
    *   **중간 산출물 캐싱:** 이미 처리된 페이지의 중간 결과물(OCR, 레이아웃 분석 결과)이 `/data/interim`에 존재할 경우, 재연산을 건너뛴다.

6.  **지속적 통합 (Continuous Integration - CI)**
    *   **GitHub Actions**를 설정하여, Git에 코드가 푸시될 때마다 다음을 자동으로 실행한다:
        1.  `pytest`: 모든 테스트 코드 실행.
        2.  `ruff`, `black --check`: 코드 포맷 및 린트 검사.
        3.  `pydantic` 스키마 검증.
    *   `git tag`가 푸시되면, 자동으로 프로젝트를 압축하여 릴리즈 아티팩트를 생성한다.

---

## **프로젝트 요구사항 (Project Requirements)**

### **1. 공식 디렉터리 구조 (Official Directory Structure)**
```
/project_root
├── /data/
│   ├── /pdf/
│   ├── /images/
│   ├── /interim/
│   └── base.json, corrected.json
├── /logs/
│   └── pipeline_*.log
├── /schema/
│   ├── schema.py
│   └── tei_header.xml
├── /prompts/
│   └── processor_*.md
├── /scripts/
│   ├── pipeline.py
│   └── ...
├── /tests/
│   ├── test_schema.py
│   ├── test_ocr_page.py
│   └── ...
├── .env, .env.example
├── .gitignore
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
└── requirements.lock
```

### **2. `requirements.txt` (최종 보강)**
```txt
# Cloud API & LLM
openai
anthropic
sentence-transformers
torch>=2.1,<2.3

# 환경 변수 관리
python-dotenv

# PDF 및 이미지 처리
PyMuPDF
opencv-python
numpy
pillow

# OCR 및 레이아웃 분석
pytesseract
layoutparser[ocr]

# 데이터 스키마 및 검증
pydantic

# 문자열 매칭
rapidfuzz

# 테스트 프레임워크
pytest
pytest-cov

# 로깅
loguru

# CLI 및 진행 상황
typer[all]
tqdm

# Jupyter 환경 (Phase 1용)
jupyterlab
notebook
```

### **3. Dockerfile (미니멀 템플릿)**
```dockerfile
FROM python:3.11-slim

# 1. 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-deu tesseract-ocr-fra \
    poppler-utils build-essential && \
    rm -rf /var/lib/apt/lists/*

# 2. Python 의존성 설치 (잠긴 버전 사용)
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock

# 3. 프로젝트 소스 복사
COPY . .

# 4. 실행
ENV PYTHONUNBUFFERED=1
CMD ["python", "scripts/pipeline.py"]
```

### **4. 초기 실행 계획 (Initial Execution Plan)**
1.  **환경 설정:** `git clone`, `poetry install` 또는 `pip install -r requirements.lock`, `.env` 파일 생성.
2.  **참조 모델 다운로드:** Fraktur `.traineddata`, `sentence-transformers` 모델 사전 다운로드.
3.  **샘플 실행 및 튜닝:** `python scripts/pipeline.py --pages 1-5 --debug` 명령으로 소량의 페이지만 처리하며 OCR 및 레이아웃 파라미터를 튜닝.
4.  **단위 테스트:** `pytest --cov=.` 실행으로 핵심 로직의 안정성 확인.
5.  **전체 실행:** `python scripts/pipeline.py`로 전체 `base.json` 생성.
6.  **강화 및 패치:** `errata_apply.py`, `toc_inject.py` 순차 실행.
7.  **최종 검증 및 패키징:** `pytest`, 스키마 검증 후 `zip`으로 압축 및 `git tag` 푸시.