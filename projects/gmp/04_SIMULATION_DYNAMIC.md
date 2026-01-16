# GMP AI 에이전트: 메타데이터 기반 동적 시뮬레이션 리포트

**작성일:** 2026-01-16
**검토자:** Smilzo (Tech Lead)
**목적:** 메타데이터 인젝션(Metadata Injection)을 통한 상황별 맞춤형 검색 범위(Scoping) 검증

## 1. 시뮬레이션 개요 (Overview)
동일한 질문("점착력 문제")이라도 사용자가 **'누구(Who)'**인지, **'어느 시장(Where)'**을 타겟으로 하는지에 따라 AI의 답변과 참조 규정이 달라져야 합니다. 본 시뮬레이션은 Vector DB 없이 메타데이터 필터링만으로 이러한 **동적 대응(Dynamic Response)**이 가능함을 검증했습니다.

### 시나리오 변수 (Variables)
1.  **Role (역할)**: 현장 작업자(Operator) vs QA 책임자(Manager)
2.  **Market (시장)**: 한국(KR/MFDS) vs 미국(US/FDA)
3.  **Output**: 긴급 행동 지침 vs 정식 CAPA 보고서

## 2. 데이터셋 구성
규제 데이터를 시장별로 구분하여 구축했습니다.

- **한국 기준 (data/regulations/mfds_*.jsonl)**: 식약처 고시 및 국내 SOP.
- **미국 기준 (data/regulations/fda_*.jsonl)**: FDA 21 CFR 211 및 Guidance.

## 3. 실행 결과 (Execution Result)

### Case A: 한국 공장 현장 작업자 (Operator @ KR)
> 긴박한 상황에서 즉시 실행할 수 있는 액션 아이템 필요

- **Input Metadata**: `{"role": "Operator", "market": "KR", "equipment": "Dryer #3"}`
- **검색 범위**: 한국 SOP 및 식약처 규정으로 자동 제한 (FDA 규정 무시)
- **AI 출력 결과**:
```text
## 🚨 현장 작업자 긴급 대응 지침
**대상 설비**: Dryer #3
**관련 제품**: BurnPatch

### [즉시 행동 요령]
✅ SOP-QA-001 준수: 4.2.3. 공정 중 일탈 처리... (즉시 확인하세요!)
✅ SOP-MF-012 준수: 7.1. 건조 온도 관리... (즉시 확인하세요!)
```

### Case B: 미국 수출팀 QA 매니저 (Manager @ US)
> FDA 감사에 대비할 수 있는 논리적 보고서 필요

- **Input Metadata**: `{"role": "QA_Manager", "market": "US", "lot_no": "EXP-2025"}`
- **검색 범위**: FDA cGMP 규정 및 가이드라인 위주 검색 (한국 SOP 후순위)
- **AI 출력 결과**:
```text
## 📑 CAPA (시정 및 예방 조치) 보고서 초안
**Report ID**: GEN-EXP-2025
**Regulatory Context**: US Market

### 1. Root Cause Analysis (Legal Basis)
- **Reference**: FDA-Guidance-Topical
  - Summary: Adhesion Failure: For transdermal systems, adhesion is a critical quality attribute (CQA)...

### 2. Risk Assessment
시스템 분석 결과, 본 건은 'Major Deviation'으로 분류될 가능성이 높습니다.
```

## 4. 결론 (Technical Implication)
메타데이터 인젝션은 단순한 필터링 이상의 가치를 제공합니다.

1.  **규제 사일로(Silo) 해결**: 하나의 시스템으로 글로벌 규제(KR, US, EU 등)를 통합 관리하되, 사용자 컨텍스트에 따라 필요한 정보만 '똑똑하게' 보여줍니다.
2.  **Persona Tuning**: 프롬프트를 따로 짜지 않아도, 메타데이터(`role`)만으로 말투와 문서 양식을 자동 전환합니다.
3.  **보안 및 효율성**: 작업자에게 불필요한(혹은 보안 등급이 높은) 문서를 원천적으로 검색 결과에서 배제할 수 있습니다.
