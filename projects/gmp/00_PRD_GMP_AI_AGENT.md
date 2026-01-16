# GMP AI 에이전트 PRD (Product Requirements Document)

**문서 버전:** 1.0
**작성일:** 2026-01-16
**작성자:** Smilzo (Tech Lead)
**상태:** Draft

---

## 1. 개요 (Executive Summary)

### 1.1 프로젝트 명
**GMP Regulatory AI Agent** (가칭: GMP-RAG)

### 1.2 프로젝트 목적
GMP 제조 현장에서 발생하는 규제 관련 질의, 일탈 대응, 신제품 인허가 등의 업무를 AI 에이전트가 보조하는 시스템 구축.

### 1.3 핵심 가치 제안
- **즉각적인 규정 검색**: 수천 페이지의 SOP/규정에서 필요한 조항을 초 단위로 검색
- **과거 사례 활용**: 유사 일탈/CAPA 이력을 자동으로 참조하여 대응 방안 제시
- **문서 초안 생성**: CAPA 보고서, 변경관리 신청서 등의 초안 자동 작성
- **규정 근거 명시**: 모든 답변에 정확한 출처(문서번호, 페이지) 인용

---

## 2. 기술 아키텍처

### 2.1 핵심 설계 원칙
> **"Vector DB 없는(Vector-less) 파일 기반 RAG 아키텍처"**

| 구성 요소 | 기술 | 역할 |
|:---|:---|:---|
| **LLM 엔진** | Antigravity (Gemini) | 질의 이해, 답변 생성, 문서 작성 |
| **검색 엔진** | ripgrep + JSONL | 정확한 키워드 매칭, 결정론적 검색 |
| **데이터 포맷** | JSONL (JSON Lines) | 사람이 읽을 수 있는 텍스트 아카이브 |
| **통합 프로토콜** | MCP (Model Context Protocol) | LLM과 검색 도구 간 표준 인터페이스 |

### 2.2 시스템 구성도

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 (QA/RA/Operator)               │
└─────────────────────────┬───────────────────────────────┘
                          │ 자연어 질의
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Antigravity (LLM Agent)                     │
│  • 질의 분석 및 맥락 이해                                │
│  • MCP Tool 호출 결정                                    │
│  • 검색 결과 종합 및 답변 생성                           │
└─────────────────────────┬───────────────────────────────┘
                          │ MCP Tool 호출
                          ▼
┌─────────────────────────────────────────────────────────┐
│              GMP MCP Server (gmp_agent)                  │
│  • search: 규정/SOP/이력 검색                            │
│  • get_chunk: 특정 문서 조회                             │
│  • list_sources: 문서 목록 반환                          │
└─────────────────────────┬───────────────────────────────┘
                          │ ripgrep 검색
                          ▼
┌─────────────────────────────────────────────────────────┐
│              GMP Archive (JSONL)                         │
│  ├── sops/           # SOP 문서 (조항별 청킹)            │
│  ├── regulations/    # 규정/고시 (조문별 청킹)           │
│  ├── history/        # 일탈/CAPA 이력                    │
│  └── manifest.json   # 문서 인덱스                       │
└─────────────────────────────────────────────────────────┘
```

### 2.3 왜 Vector DB가 아닌가?

| 비교 항목 | Vector DB | 파일 기반 (JSONL + Grep) |
|:---|:---|:---|
| 검색 방식 | 의미적 유사성 (확률적) | **정확한 매칭 (결정적)** |
| 데이터 무결성 | 블랙박스 | **사람이 검증 가능** |
| CSV 대응 | 어려움 | **유리함** |
| 인프라 비용 | DB 서버 필요 | **폴더만 있으면 됨** |

---

## 3. 데이터 구조

### 3.1 청킹 전략 (문서 유형별)

| 문서 유형 | 청킹 단위 | 예시 |
|:---|:---|:---|
| SOP | 조항(Section) | "4.2 일탈 처리 절차" |
| 규정/고시 | 조문(Article) | "제22조(시험검사)" |
| 제조기록서 | 페이지 | "Lot 240115, p.12" |
| 일탈보고서 | 문서 전체 | "DEV-230205" |

### 3.2 청크 스키마

```json
{
  "global_chunk_id": "SOP-QA-001:4.2",
  "doc_id": "SOP-QA-001",
  "doc_type": "sop",
  "section": "4.2",
  "content": "CQA가 기준치 미만일 경우 즉시 격리 조치...",
  "page_range": [3, 4],
  "citation": "SOP-QA-001, 4.2 (p.3-4)",
  "revision_date": "2025-01-15"
}
```

### 3.3 예상 데이터 규모

| 항목 | 규모 | 비고 |
|:---|:---|:---|
| 문서 수 | ~1,000개 | SOP, 규정, 이력 포함 |
| 총 페이지 | ~10,000장 | A4 기준 |
| 데이터 크기 | ~50MB | JSONL 변환 후 |
| 검색 응답 시간 | < 50ms | ripgrep 기준 |

---

## 4. 기능 요구사항

### 4.1 핵심 기능 (MVP)

| 기능 | 설명 | 우선순위 |
|:---|:---|:---|
| **규정 검색** | 키워드로 SOP/규정 조회, 근거 인용 | P0 |
| **일탈 대응** | 과거 유사 사례 검색 및 CAPA 제안 | P0 |
| **문서 초안** | CAPA 보고서, 변경관리 신청서 초안 생성 | P1 |
| **인허가 분석** | 신제품 허가 필요 서류 리스트 도출 | P1 |

### 4.2 MCP Tool 명세

| Tool | 입력 | 출력 | 용도 |
|:---|:---|:---|:---|
| `search` | query, market, doc_type | 매칭된 청크 리스트 | 규정/SOP 검색 |
| `get_chunk` | doc_id | 문서 전체 내용 | 상세 조회 |
| `list_sources` | market | 문서 메타데이터 리스트 | 문서 목록 |

### 4.3 동적 대응 (메타데이터 기반)

| 메타데이터 | 효과 |
|:---|:---|
| `role: Operator` | 긴급 행동 지침 스타일 |
| `role: QA_Manager` | 정식 보고서 스타일 |
| `market: KR` | 식약처 규정 우선 검색 |
| `market: US` | FDA 규정 우선 검색 |

---

## 5. 인프라 및 네트워킹

### 5.1 운용 환경

| 항목 | 사양 |
|:---|:---|
| **운영체제** | macOS (Antigravity 호환) |
| **LLM 엔진** | Antigravity (로컬 실행) |
| **Python** | 3.11+ (shared_venv) |
| **검색 도구** | ripgrep (brew install ripgrep) |

### 5.2 사무실 내부 네트워킹 제안

**Option A: 단일 사용자 (현재)**
```
[User Mac] ← Antigravity + MCP Server + Archive (All Local)
```
- 설정: 없음 (현재 상태)
- 장점: 단순, 데이터 유출 위험 없음

**Option B: 소규모 팀 (3-5명)**
```
[NAS/공유폴더]
     ↑ SMB/AFP 마운트
┌────┴────┐
│ User A  │ ← 각자 Antigravity + MCP Server 실행
│ User B  │    Archive는 공유폴더 참조
│ User C  │
└─────────┘
```
- 설정: NAS에 `gmp_archive/` 폴더 생성, 각 Mac에서 마운트
- 장점: 데이터 동기화 자동화, 동시 접근 가능
- 권장 NAS: Synology DS220+ 또는 QNAP

**Option C: 중규모 팀 (10명+)**
```
[사내 서버]
  └── MCP Server (단일 인스턴스)
       ↑ HTTP/WebSocket
┌──────┴──────┐
│ User A~J   │ ← Antigravity에서 원격 MCP 호출
└─────────────┘
```
- 설정: 별도 서버에 MCP Server 배포
- 장점: 중앙 집중 관리, 버전 통일
- 고려사항: 네트워크 지연, 서버 관리 인력 필요

### 5.3 권장 구성 (귀사 규모)

> **Option B (소규모 팀) 권장**
> - NAS에 Archive 저장
> - 각 사용자 Mac에서 Antigravity + MCP Server 로컬 실행
> - NAS 폴더를 SMB로 마운트하여 Archive 공유

---

## 6. 보안 및 백업

### 6.1 데이터 보안

| 항목 | 현재 상태 | 권장 |
|:---|:---|:---|
| 데이터 저장 | 로컬 (Mac) | ✅ 유지 (외부 전송 없음) |
| LLM API 호출 | Antigravity (로컬) | ✅ 데이터 외부 유출 없음 |
| 접근 제어 | 없음 | 🟡 macOS 사용자 권한 활용 |

### 6.2 백업 전략 (Dropbox 활용)

```
[로컬 Archive]
     │
     │ Dropbox Sync
     ▼
[Dropbox Cloud]
     │
     │ 버전 관리 (30일)
     ▼
[복구 가능]
```

**권장 설정:**
1. `gmp_archive/` 폴더를 Dropbox 폴더 내에 위치
2. Dropbox 선택적 동기화로 필요한 폴더만 로컬에 유지
3. 중요 문서 변경 시 자동 버전 기록 (Dropbox 기본 기능)

### 6.3 재해 복구 (Disaster Recovery)

| 시나리오 | 복구 방법 | RTO |
|:---|:---|:---|
| 파일 삭제 | Dropbox 버전 복원 | 5분 |
| Mac 고장 | Dropbox에서 재동기화 | 1시간 |
| Dropbox 장애 | 로컬 Time Machine 복원 | 2시간 |

---

## 7. 구현 로드맵

### Phase 1: 데이터 준비 (2주)
- [ ] 기존 SOP/규정 PDF 수집 및 정리
- [ ] 문서 유형별 분류 (sop, regulation, history)
- [ ] 청킹 파이프라인 구축 (PDF → JSONL)
- [ ] 메타데이터 태깅 (문서번호, 개정일, 페이지)

### Phase 2: MCP Server 개발 (1주)
- [ ] `gmp_server.py` 구현
- [ ] `search`, `get_chunk`, `list_sources` Tool 개발
- [ ] Antigravity 설정 (`settings.json`)
- [ ] 통합 테스트

### Phase 3: 파일럿 운영 (4주)
- [ ] QA팀 대상 파일럿
- [ ] 피드백 수집 및 개선
- [ ] 추가 문서 인제스천

### Phase 4: 확장 및 안정화 (지속)
- [ ] 전사 확대
- [ ] NAS 공유 환경 구축
- [ ] 사용자 교육

---

## 8. 리스크 및 대응

| 리스크 | 영향 | 대응 방안 |
|:---|:---|:---|
| OCR 품질 저하 | 검색 누락 | 스캔 문서 재처리, 수동 검수 |
| 문서 업데이트 누락 | 잘못된 정보 제공 | 개정 문서 자동 감지 워크플로우 |
| LLM Hallucination | 잘못된 규정 인용 | 근거 없는 답변 차단, 출처 필수 |
| 대용량 성능 저하 | 검색 지연 | ripgrep 병렬화, 파일 분할 |

---

## 9. 참조 문서 (부록)

본 PRD는 다음 문서들을 기반으로 작성되었습니다:

| 번호 | 문서명 | 내용 |
|:---|:---|:---|
| 01 | `01_TECHNICAL_REVIEW_ARCHITECTURE.pdf` | 아키텍처 설계 및 MCP 통합 |
| 02 | `02_SIMULATION_DEVIATION.pdf` | 공정 일탈 대응 시뮬레이션 |
| 03 | `03_SIMULATION_RA.pdf` | 신제품 인허가 시뮬레이션 |
| 04 | `04_SIMULATION_DYNAMIC.pdf` | 메타데이터 동적 대응 시뮬레이션 |
| 05 | `05_SELF_EVALUATION.pdf` | PoC 자체 평가 |
| 06 | `06_CHUNKING_STRATEGY.pdf` | 문서 청킹 전략 |

---

## 10. 추가 필요 섹션 (향후 보완)

| 섹션 | 필요성 | 담당 |
|:---|:---|:---|
| **사용자 매뉴얼** | 실제 운영 시 필수 | 운영팀 |
| **CSV 밸리데이션 계획** | GMP 규제 대응 | QA팀 |
| **SLA 정의** | 시스템 가용성/응답시간 보장 | IT팀 |
| **교육 계획** | 사용자 온보딩 | HR/운영팀 |
| **비용 분석** | NAS, 인력 등 TCO | 경영팀 |

---

## 11. CSV (Computer System Validation) 계획

### 11.1 규제 근거

| 규정 | 핵심 요구사항 |
|:---|:---|
| **FDA 21 CFR Part 11** | 전자기록/전자서명의 신뢰성 보장 |
| **EU GMP Annex 11** | 컴퓨터화 시스템 검증 |
| **MFDS 의약품 제조 및 품질관리 기준** | 컴퓨터화 시스템의 밸리데이션 |
| **PIC/S PI 011-3** | GMP 환경 컴퓨터 시스템 가이드 |

### 11.2 시스템 분류 (GAMP 5)

| 항목 | 분류 | 근거 |
|:---|:---|:---|
| **Antigravity (LLM)** | Category 5 (Custom) | AI/ML 기반 커스텀 로직 |
| **MCP Server** | Category 5 (Custom) | 자체 개발 Python 서버 |
| **ripgrep** | Category 3 (COTS) | 오픈소스 검색 도구 |
| **JSONL Archive** | Category 1 (Infrastructure) | 파일 시스템 기반 데이터 저장 |

### 11.3 CSV 문서 체계

```
CSV 문서 패키지
├── VP (Validation Plan)           # 검증 계획서
├── URS (User Requirement Spec)    # 사용자 요구사양 (본 PRD 기반)
├── FS (Functional Spec)           # 기능 명세서
├── DS (Design Spec)               # 설계 명세서
├── IQ (Installation Qual.)        # 설치 적격성
├── OQ (Operational Qual.)         # 운전 적격성
├── PQ (Performance Qual.)         # 성능 적격성
├── RTM (Requirements Trace Matrix)# 요구사항 추적 매트릭스
└── VR (Validation Report)         # 검증 보고서
```

### 11.4 검증 범위

| 구성요소 | IQ | OQ | PQ | 비고 |
|:---|:---|:---|:---|:---|
| MCP Server 설치 | ✅ | - | - | Python 버전, 의존성 확인 |
| `search` Tool | - | ✅ | ✅ | 검색 정확도 검증 |
| `get_chunk` Tool | - | ✅ | - | 문서 반환 정확성 |
| `list_sources` Tool | - | ✅ | - | 목록 완전성 |
| JSONL Archive | ✅ | ✅ | - | 파일 무결성, 스키마 준수 |
| 전체 시스템 | - | - | ✅ | 실제 업무 시나리오 테스트 |

### 11.5 CSV 일정

| 단계 | 기간 | 산출물 |
|:---|:---|:---|
| 계획 수립 | 1주 | VP, URS |
| 설계 문서화 | 1주 | FS, DS |
| IQ 수행 | 3일 | IQ Protocol/Report |
| OQ 수행 | 1주 | OQ Protocol/Report, RTM |
| PQ 수행 | 2주 | PQ Protocol/Report |
| 최종 보고 | 3일 | VR, 승인 |

---

## 12. 데이터 무결성 (Data Integrity) 보장 방안

### 12.1 ALCOA+ 원칙 준수 매핑

| 원칙 | 정의 | 본 시스템 대응 방안 |
|:---|:---|:---|
| **A**ttributable | 누가 작성/수정했는지 확인 가능 | JSONL 메타데이터에 `author`, `revision_by` 필드 포함 |
| **L**egible | 읽을 수 있고 영구적 | JSONL = 사람이 읽을 수 있는 텍스트 포맷 |
| **C**ontemporaneous | 실시간 기록 | 문서 개정 시 `revision_date` 자동 타임스탬프 |
| **O**riginal | 원본 또는 인증된 사본 | 원본 PDF와 JSONL 청크 간 `source_hash` 매핑 |
| **A**ccurate | 정확하고 오류 없음 | 청킹 후 수동 검수, 스키마 밸리데이션 |
| **+Complete** | 완전함 | 문서 전체가 청킹됨, 누락 체크리스트 |
| **+Consistent** | 일관성 | JSON Schema 강제, 문서 유형별 템플릿 |
| **+Enduring** | 영구 보존 | Dropbox 백업, Time Machine |
| **+Available** | 필요 시 접근 가능 | ripgrep 즉시 검색, NAS 공유 |

### 12.2 감사 추적 (Audit Trail) 구현

**현재 상태 (JSONL 기반):**

```json
{
  "global_chunk_id": "SOP-QA-001:4.2:v3",
  "doc_id": "SOP-QA-001",
  "version": 3,
  "revision_date": "2025-01-15T09:30:00+09:00",
  "revision_by": "김품질",
  "revision_reason": "일탈 처리 시한 변경 (24h → 48h)",
  "previous_version_id": "SOP-QA-001:4.2:v2",
  "content": "..."
}
```

**권장 개선 (Phase 2):**

| 항목 | 현재 | 개선안 |
|:---|:---|:---|
| 변경 이력 | JSONL 필드 내 기록 | 별도 `audit_log.jsonl` 분리 |
| 삭제 기록 | 미지원 | Soft Delete + 삭제 로그 |
| 검색 로그 | 미지원 | `query_log.jsonl` 추가 |

### 12.3 무결성 검증 도구

```bash
# 스키마 검증 (Phase 1)
python validate_schema.py --archive ./gmp_archive/

# 해시 검증 (Phase 2) 
python verify_hash.py --source ./originals/ --archive ./gmp_archive/
```

---

## 13. 변경 관리 (Change Control) 절차

### 13.1 변경 유형 분류

| 유형 | 정의 | 예시 | 승인 수준 |
|:---|:---|:---|:---|
| **Type A (Minor)** | 문서/데이터 수정, 기능 변경 없음 | SOP 오타 수정, 메타데이터 보완 | QA 담당자 |
| **Type B (Major)** | 기능 변경 또는 신규 문서 추가 | 새 규정 인제스천, MCP Tool 수정 | QA 책임자 |
| **Type C (Critical)** | 아키텍처 변경 또는 시스템 교체 | LLM 엔진 변경, 검색 로직 변경 | QA 책임자 + 경영진 |

### 13.2 변경 관리 워크플로우

```
┌─────────────┐
│ 변경 요청서  │  (Change Request Form)
│ 작성        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 영향 분석   │  Impact Assessment
│ (IA)       │  - 영향 받는 문서 목록
└──────┬──────┘  - 재검증 범위 결정
       │
       ▼
┌─────────────┐
│ 변경 승인   │  (Type별 승인권자)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 변경 실행   │  - JSONL 업데이트
│            │  - 코드 수정 (필요시)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 재검증     │  (영향 범위에 따라 IQ/OQ/PQ)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 변경 종료   │  Change Control Record 완료
└─────────────┘
```

### 13.3 문서 개정 관리

| 항목 | 규칙 |
|:---|:---|
| **버전 번호** | Major.Minor (예: 2.1) |
| **개정 이력** | JSONL 내 `revision_history` 배열 |
| **유효 버전** | `status: "current"` 플래그로 구분 |
| **구버전 보관** | `/archive/deprecated/` 폴더로 이동 (삭제 금지) |

### 13.4 긴급 변경 (Emergency Change)

| 조건 | 절차 |
|:---|:---|
| 규정 위반 발견 | 즉시 수정 → 사후 승인 (24시간 내) |
| 시스템 장애 | 복구 우선 → 변경 요청서 소급 작성 |

---

## 14. Hallucination 방지 메커니즘

### 14.1 기본 원칙

> **"검색 결과가 없으면, 모른다고 답한다."**

### 14.2 기술적 방지책

| 레이어 | 방지책 | 구현 방법 |
|:---|:---|:---|
| **MCP Server** | 검색 결과 없음 명시 | `{"results": [], "message": "No matching documents found"}` 반환 |
| **Prompt** | 출처 필수 강제 | System Prompt에 "You MUST cite document ID" 명시 |
| **Prompt** | 불확실성 표현 강제 | "확인된 규정 없음" 등 표준 문구 사용 |
| **Post-processing** | Citation 검증 | 응답 내 인용된 doc_id가 실제 존재하는지 검증 |

### 14.3 System Prompt 템플릿

```markdown
## GMP AI Agent 행동 규칙

1. **출처 필수**: 모든 규정/절차 인용 시 반드시 문서번호와 조항을 명시하라.
   - ✅ "SOP-QA-001, 4.2항에 따르면..."
   - ❌ "일반적으로 GMP에서는..."

2. **불확실성 인정**: 검색 결과가 없거나 불충분하면 명확히 밝혀라.
   - ✅ "관련 규정을 찾지 못했습니다. QA팀에 문의하세요."
   - ❌ (규정을 지어내는 행위)

3. **범위 제한**: 본 시스템은 {market} 시장의 {doc_types} 문서만 검색 가능함.
   - 범위 외 질문: "해당 정보는 본 시스템 검색 범위를 벗어납니다."

4. **최신성 주의**: 검색된 문서의 revision_date를 확인하고 알려라.
   - "본 답변은 2025-01-15 개정 기준입니다."
```

### 14.4 Hallucination 모니터링

| 지표 | 측정 방법 | 목표 |
|:---|:---|:---|
| **Citation Rate** | (출처 있는 답변 / 전체 답변) × 100 | > 95% |
| **False Citation Rate** | (존재하지 않는 doc_id 인용 / 전체 인용) × 100 | < 1% |
| **Refusal Rate** | ("모름" 답변 / 전체 답변) × 100 | 5-15% (너무 낮으면 의심) |

---

## 15. 프롬프트 엔지니어링 가이드라인

### 15.1 표준 응답 형식

**규정 검색 응답:**
```
## 검색 결과

**질의:** {user_query}
**검색 범위:** {market} / {doc_types}

### 관련 규정

1. **[SOP-QA-001, 4.2항]** 일탈 처리 절차
   > "CQA가 기준치 미만일 경우 즉시 격리 조치..."
   - 개정일: 2025-01-15

2. **[REG-MFDS-001, 제22조]** 시험검사
   > ...

### 권장 조치
- ...

### 주의사항
- 본 답변은 AI가 생성한 것으로, 최종 결정은 QA 책임자가 내려야 합니다.
```

### 15.2 언어 정책

| 상황 | 언어 | 비고 |
|:---|:---|:---|
| 사용자 질의 (한국어) | 한국어 응답 | 기본값 |
| 사용자 질의 (영어) | 영어 응답 | 자동 감지 |
| FDA 규정 인용 | 영어 원문 + 한국어 요약 | 번역 오류 방지 |
| 식약처 규정 인용 | 한국어 원문 | - |

### 15.3 금지 표현 (Blacklist)

| 금지 표현 | 대체 표현 |
|:---|:---|
| "일반적으로", "보통", "대개" | (구체적 규정 인용) |
| "~일 것입니다", "~라고 생각합니다" | "~에 따르면", "~라고 규정되어 있습니다" |
| "인터넷에서 확인한 바로는" | (시스템 내 문서만 참조) |
| "GMP 규정에 의하면" (모호함) | "[SOP-XX-000, X조]에 의하면" |

### 15.4 역할별 응답 톤

| 역할 | 톤 | 특징 |
|:---|:---|:---|
| `Operator` | 명령형, 간결 | "즉시 ~하십시오", 체크리스트 형태 |
| `QA_Manager` | 분석적, 상세 | 근거 다수 인용, 옵션 제시 |
| `RA_Specialist` | 규제 중심, 전문적 | 규정 조문 정확 인용, 국가별 비교 |

---

## 16. 테스트 및 품질관리 (QA Plan)

### 16.1 테스트 전략 개요

| 단계 | 목적 | 수행 시점 |
|:---|:---|:---|
| **Unit Test** | 개별 함수/Tool 정상 동작 | 개발 중 |
| **Integration Test** | MCP Server ↔ Archive 연동 | 개발 완료 후 |
| **IQ** | 설치 환경 적격성 | 배포 전 |
| **OQ** | 기능 정상 동작 | 배포 후 |
| **PQ** | 실제 업무 시나리오 수행 | 파일럿 기간 |
| **Regression Test** | 변경 후 기존 기능 유지 | 매 변경 시 |

### 16.2 IQ (Installation Qualification) 체크리스트

| 항목 | 검증 내용 | Pass 기준 |
|:---|:---|:---|
| Python 버전 | `python --version` | 3.11.x |
| 의존성 설치 | `pip list` | requirements.txt 일치 |
| ripgrep 설치 | `rg --version` | 14.0+ |
| Archive 경로 | 폴더 존재 확인 | `./gmp_archive/` 존재 |
| MCP Server 기동 | `python gmp_server.py` | 오류 없이 시작 |

### 16.3 OQ (Operational Qualification) 테스트 케이스

| TC ID | 테스트 항목 | 입력 | 기대 결과 |
|:---|:---|:---|:---|
| OQ-001 | search 기본 | `{"query": "일탈"}` | 1개 이상 결과 반환 |
| OQ-002 | search 없음 | `{"query": "xyz123존재안함"}` | 빈 배열 반환 |
| OQ-003 | get_chunk | `{"doc_id": "SOP-QA-001"}` | 전체 문서 내용 반환 |
| OQ-004 | get_chunk 없음 | `{"doc_id": "INVALID"}` | 에러 메시지 반환 |
| OQ-005 | list_sources | `{"market": "KR"}` | 문서 목록 반환 |
| OQ-006 | market 필터 | `search` with `market: US` | FDA 문서만 반환 |
| OQ-007 | doc_type 필터 | `search` with `doc_type: sop` | SOP만 반환 |

### 16.4 PQ (Performance Qualification) 시나리오

| 시나리오 | 상세 | 성공 기준 |
|:---|:---|:---|
| **PQ-001: 일탈 대응** | "공정 중 온도 일탈 발생, 대응 방법?" | 관련 SOP 인용, 과거 사례 제시, CAPA 제안 |
| **PQ-002: 규정 검색** | "시험검사 관련 식약처 규정 찾아줘" | 정확한 조문 인용, 출처 명시 |
| **PQ-003: 문서 초안** | "온도 일탈 CAPA 보고서 초안 작성" | 표준 양식 준수, 빈칸 없음 |
| **PQ-004: 다국적 비교** | "FDA vs 식약처 안정성 시험 규정 비교" | 양국 규정 정확 인용 |

### 16.5 검색 품질 지표

| 지표 | 정의 | 목표 |
|:---|:---|:---|
| **Precision** | (관련 결과 / 반환 결과) × 100 | > 90% |
| **Recall** | (반환된 관련 결과 / 전체 관련 문서) × 100 | > 85% |
| **MRR** | 첫 번째 관련 결과의 순위 역수 평균 | > 0.8 |
| **응답 시간** | 검색 ~ 결과 반환 | < 100ms |

---

## 17. Glossary (용어 정의)

### 17.1 GMP 관련 용어

| 용어 | 정의 |
|:---|:---|
| **GMP** | Good Manufacturing Practice. 의약품 제조 및 품질관리 기준. |
| **SOP** | Standard Operating Procedure. 표준작업절차서. |
| **CAPA** | Corrective and Preventive Action. 시정 및 예방 조치. |
| **일탈 (Deviation)** | 승인된 절차, 기준 또는 규격에서 벗어난 상태. |
| **CQA** | Critical Quality Attribute. 핵심품질특성. |
| **QA** | Quality Assurance. 품질보증. |
| **RA** | Regulatory Affairs. 인허가 업무. |
| **CSV** | Computer System Validation. 컴퓨터화 시스템 검증. |
| **ALCOA+** | Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available. 데이터 무결성 원칙. |
| **FDA** | U.S. Food and Drug Administration. 미국 식품의약국. |
| **MFDS** | Ministry of Food and Drug Safety. 식품의약품안전처 (식약처). |
| **PIC/S** | Pharmaceutical Inspection Co-operation Scheme. 의약품 실사 상호협력기구. |

### 17.2 기술 관련 용어

| 용어 | 정의 |
|:---|:---|
| **LLM** | Large Language Model. 대규모 언어 모델 (예: GPT, Gemini). |
| **RAG** | Retrieval-Augmented Generation. 검색 증강 생성. 외부 데이터를 검색하여 LLM 답변에 활용하는 기법. |
| **MCP** | Model Context Protocol. LLM과 외부 도구 간 표준 통신 프로토콜. |
| **JSONL** | JSON Lines. 각 줄이 독립적인 JSON 객체인 텍스트 파일 포맷. |
| **ripgrep (rg)** | 초고속 텍스트 검색 도구. `grep`의 현대적 대안. |
| **청킹 (Chunking)** | 큰 문서를 검색/처리에 적합한 작은 단위로 분할하는 과정. |
| **Vector DB** | 텍스트 임베딩을 저장하고 유사성 검색을 수행하는 데이터베이스. |
| **Hallucination** | LLM이 사실이 아닌 정보를 생성하는 현상. |
| **Antigravity** | Google Gemini 기반의 AI 코딩 에이전트 플랫폼. |

### 17.3 검증 관련 용어 (GAMP 5)

| 용어 | 정의 |
|:---|:---|
| **GAMP 5** | Good Automated Manufacturing Practice. ISPE의 컴퓨터화 시스템 검증 가이드. |
| **IQ** | Installation Qualification. 설치 적격성 검증. |
| **OQ** | Operational Qualification. 운전 적격성 검증. |
| **PQ** | Performance Qualification. 성능 적격성 검증. |
| **URS** | User Requirement Specification. 사용자 요구사양서. |
| **RTM** | Requirements Traceability Matrix. 요구사항 추적 매트릭스. |

---

**문서 끝**
