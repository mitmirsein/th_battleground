# Kerygma Daily 생성 파이프라인

> **목적**: AI 에이전트(Antigravity)를 통한 순차적 월간 묵상 데이터 생성

---

## 파이프라인 개요

```
[RCL 본문] → [1단계] → [2단계] → [3단계] → [4단계] → [5단계] → [최종 JSON]
              선정      기초      묵상      검증      조립
```

| 단계 | 명칭 | 작업 단위 | 설명 |
|:---:|:---:|:---:|:---|
| 1 | 본문 선정 | 주 단위 | RCL에서 OT/NT 각 1절 선정 |
| 2 | 기초 작업 | 주 단위 | 원어 파싱, 직역, 키워드 |
| 3 | 묵상 작업 | 주 단위 | 신학적 묵상, 적용 질문 |
| 4 | 검증 작업 | 월 단위 | JSON 구조 및 품질 검증 |
| 5 | 조립 작업 | 월 단위 | 최종 JSON 병합 및 배포 |

---

## 폴더 구조

```
/Kerygma_Pipeline/
├── 00_rcl_input/           # RCL 본문 입력
│   └── 2026-02_RCL_Readings.md
├── 01_selection/           # 1단계 출력
│   └── week1~4_selection.json
├── 02_foundation/          # 2단계 출력
│   └── week1~4_foundation.json
├── 03_meditation/          # 3단계 출력
│   └── week1~4_meditation.json
├── 04_verified/            # 4단계 출력
│   └── 2026-02_verified.json
└── 05_final/               # 5단계 출력
    └── 2026-02.json
```

---

## 실행 방법

### 준비
1. RCL 본문을 `00_rcl_input/` 폴더에 준비
2. Antigravity에서 각 단계를 순차적으로 실행

### 순차 실행 순서
```
1단계 Week1 → 1단계 Week2 → 1단계 Week3 → 1단계 Week4
    ↓
2단계 Week1 → 2단계 Week2 → 2단계 Week3 → 2단계 Week4
    ↓
3단계 Week1 → 3단계 Week2 → 3단계 Week3 → 3단계 Week4
    ↓
4단계 (전체 검증)
    ↓
5단계 (최종 조립)
```

### 실행 명령어 예시
```
"1단계 1주차 실행"
"2단계 전체 실행"
"3단계 2주차 진행"
"4단계 검증 작업 실행"
"5단계 작업 실행"
```

---

## 단계별 지시서

### 📋 1단계: 본문 선정 (Selector)

```
[역할] 본문 선정 담당자

[입력] 
- RCL 본문: {00_rcl_input/} 중 Week {N}

[작업]
1. 해당 주간 각 날짜별 RCL 본문 검토
2. 구약 1구절, 신약 1구절 선정
3. 선정 이유 간략 기술

[출력 필드]
- date, liturgical, ot_ref, nt_ref, selection_reason

[저장] 01_selection/week{N}_selection.json
```

---

### 📋 2단계: 기초 작업 (Exegete)

```
[역할] 원어 주석 담당자

[입력]
- 1단계 결과: {01_selection/week{N}_selection.json}
- 표준 샘플: {data/2026-01.json}

[작업]
각 날짜에 대해:
1. 원문 추출: 히브리어(OT), 헬라어(NT)
2. 단어 파싱: text, sound(한글 음역), lemma, lemma_sound(기본형 음역), morph, gloss
3. 번역 작성:
   - kor_std (개역한글)
   - kor_lit (직역, "한글(음역)" 포맷)
   - eng_bsb (Berean Standard Bible) ← 필수
4. 메타 필드:
   - lang_class: "hebrew" 또는 "greek" ← 필수
5. 키워드: keywords 배열 (5개 내외)

[출력 구조]
{
  "ot": {
    "ref": "창세기 1:1",
    "lang": "hebrew",
    "lang_class": "hebrew",
    "text_dir": "rtl",
    "kor_std": "...",
    "kor_lit": "...",
    "eng_bsb": "...",
    "focus_text": "...",
    "words": [
      {
        "text": "...",
        "sound": "...",
        "lemma": "...",
        "lemma_sound": "...",
        "morph": "...",
        "gloss": "..."
      }
    ]
  },
  "nt": { ... },
  "keywords": [...]
}

[저장] 02_foundation/week{N}_foundation.json
```

---

### 📋 3단계: 묵상 작업 (Homilist)

```
[역할] 묵상 집필자

[입력]
- 2단계 결과: {02_foundation/week{N}_foundation.json}
- 생성 지침: {GENERATION_GUIDELINES.md}

[작업]
1. 신학적 연결: OT-NT 상호 조명
2. 묵상글 작성:
   - 원어 인용: "한글 의미('음역')" 포맷
   - 마지막 문장: 위로, 희망, 평안 지향
3. 성찰 질문:
   - 양자택일형 금지
   - 건설적, 부드러운 질문

[핵심 원칙]
> 독자에게 위로, 격려, 희망, 평안의 메시지를 전달

[출력 구조]
{
  "date": "...",
  "liturgical": "...",
  "title": "...",
  "ot": { "ref", "focus_word", "focus_sound", "focus_meaning" },
  "nt": { "ref", "focus_word", "focus_sound", "focus_meaning" },
  "meditation": "...",
  "reflection": "..."
}

[저장] 03_meditation/week{N}_meditation.json
```

---

### 📋 4단계: 검증 작업 (Validator)

```
[역할] 품질 검증관

[입력]
- 1~3단계 결과 전체
- RCL 원본, 생성 지침

[검증 항목]
1. JSON 구조 유효성
2. 필수 필드 완전성 (eng_bsb, lang_class 포함)
3. 28일 데이터 완전성
4. 묵상 톤 검증 (부정적 질문 없음)
5. 직역 포맷 검증 ("한글(음역)")

[출력] 검증 통과 선언 또는 수정 사항 리포트
[저장] 04_verified/2026-02_verified.json
```

---

### 📋 5단계: 조립 작업 (Assembler)

```
[역할] 최종 조립자

[입력]
- 4단계 검증 완료 데이터
- 표준 샘플: {data/2026-01.json}

[작업]
1. foundation + meditation 병합
2. metadata 섹션 추가 (version, generated)
3. 날짜 순 정렬
4. 배포 폴더에 복사

[출력 위치]
- Kerygma_Pipeline/05_final/2026-02.json
- data/2026-02.json (프로젝트 루트)
```

---

## 체크리스트

- [ ] RCL 본문 준비 완료
- [ ] 1단계: 전체 주간 선정 완료
- [ ] 2단계: 전체 주간 기초 작업 완료
- [ ] 3단계: 전체 주간 묵상 작업 완료
- [ ] 4단계: 검증 통과
- [ ] 5단계: 최종 JSON 생성
- [ ] GitHub 푸시
- [ ] Netlify 배포 확인

---

*Updated: 2026-01-05*
