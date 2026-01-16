# GMP 문서 청킹 전략 가이드

**작성일:** 2026-01-16
**검토자:** Smilzo (Tech Lead)
**목적:** GMP 문서 유형별 최적화된 청킹(Chunking) 전략 정의

## 1. 핵심 원칙

> **"문서 유형(doc_type)을 먼저 구분하고, 유형별로 다른 청킹 전략을 적용한다."**

```
[문서 인제스천 흐름]

1️⃣ 문서 유형 판별
   "이 파일은 SOP인가? 규정인가? 일탈보고서인가?"
   → 파일명/폴더 위치/메타데이터로 자동 또는 수동 판별

2️⃣ 유형별 청킹 전략 적용
   - SOP → 조항(4.2, 4.3...) 단위로 분할
   - 규정 → 조문(제9조, 제22조...) 단위로 분할
   - 일탈보고서 → 문서 전체를 하나로

3️⃣ 동일 포맷(JSONL)으로 저장
   모든 청크는 동일한 스키마로 저장
```

## 2. 문서 유형별 특성 분석

| 문서 유형 | 특성 | 예시 | 권장 청킹 단위 |
|:---|:---|:---|:---|
| **SOP (표준운영절차)** | 조항별 구조, 번호 체계 명확 | SOP-QA-001 | **조항(Section) 단위** |
| **규정/고시** | 조/항/호 법적 구조 | 식약처 고시 제22조 | **조(Article) 단위** |
| **제조기록서 (BMR)** | 페이지별 독립적 기록 | Batch Record | **페이지 단위** |
| **일탈/CAPA 보고서** | 전체가 하나의 맥락 | Deviation Report | **문서 전체** |
| **밸리데이션 프로토콜** | 섹션별 구분 명확 | IQ/OQ/PQ | **섹션 단위** |

## 3. 왜 페이지 단위가 아닌가?

| 상황 | 페이지 단위 청킹 | 조항 단위 청킹 |
|:---|:---|:---|
| "4.2항 내용 알려줘" | 2페이지에 걸쳐 있으면 맥락 잘림 | 완전한 조항 반환 |
| 인용 시 | "p.3-4" (애매함) | **"4.2항 (p.3-4)"** (정확함) |

**핵심:**
> **"페이지가 아니라 의미 단위(Semantic Unit)로 청킹하되, 인용은 페이지로"**

## 4. 청킹 프리셋 정의

```yaml
# chunking_presets.yaml
presets:
  sop:
    strategy: section
    section_pattern: "^\\d+\\.\\d+"   # "4.2", "5.1.3" 등
    fallback_size: 1500               # 조항이 너무 길면 분할
    overlap: 200
    metadata:
      - section_number
      - page_range
      - revision_date
    
  regulation:
    strategy: article
    article_pattern: "^제\\d+조"       # "제22조", "제5조의2" 등
    fallback_size: 2000
    overlap: 300
    metadata:
      - article_number
      - effective_date
    
  batch_record:
    strategy: page
    page_size: 1                       # 1페이지 = 1청크
    overlap: 0
    metadata:
      - page_number
      - lot_number
      - process_step
    
  deviation_report:
    strategy: document
    max_size: 10000                    # 문서 전체 = 1청크
    metadata:
      - deviation_id
      - product
      - severity
```

## 5. 청킹 파이프라인 (코드 예시)

```python
def chunk_gmp_document(pdf_path, doc_type):
    """
    GMP 문서 유형별 최적 청킹
    """
    preset = load_preset(doc_type)
    pages = extract_pages(pdf_path)
    
    # 전략별 청킹
    if preset.strategy == "section":
        chunks = chunk_by_section(pages, preset.section_pattern)
    elif preset.strategy == "article":
        chunks = chunk_by_article(pages, preset.article_pattern)
    elif preset.strategy == "page":
        chunks = chunk_by_page(pages)
    else:  # document
        chunks = [{"content": "\n".join(pages), "page_range": [1, len(pages)]}]
    
    # 메타데이터 태깅
    for chunk in chunks:
        chunk["doc_id"] = generate_doc_id(pdf_path)
        chunk["citation"] = generate_citation(chunk, preset)
    
    return chunks
```

## 6. 인용(Citation) 생성 규칙

| 문서 유형 | 인용 포맷 | 예시 |
|:---|:---|:---|
| **SOP** | `{doc_id}, {section} (p.{pages})` | `SOP-QA-001, 4.2.3 (p.4)` |
| **규정** | `{title}, {article}` | `의약외품 품목허가 규정, 제9조` |
| **BMR** | `{lot_no}, p.{page}` | `Lot 240115, p.12` |
| **일탈보고서** | `{deviation_id}` | `DEV-230205` |

## 7. 권장 폴더 구조

```
gmp_archive/
├── chunks/
│   ├── sops/
│   │   ├── SOP-QA-001.jsonl    # 조항별 청킹
│   │   └── SOP-MF-012.jsonl
│   ├── regulations/
│   │   ├── MFDS-2025-32.jsonl  # 조문별 청킹
│   │   └── FDA-21CFR-211.jsonl
│   ├── batch_records/
│   │   └── 2025/
│   │       └── Lot_240115.jsonl  # 페이지별 청킹
│   └── deviations/
│       └── DEV-230205.jsonl      # 문서 전체
└── manifest.json
```

## 8. 청크 데이터 스키마 (JSONL)

```json
{
  "global_chunk_id": "SOP-QA-001:4.2",
  "doc_id": "SOP-QA-001",
  "doc_type": "sop",
  "section": "4.2",
  "title": "일탈 처리 절차",
  "content": "CQA가 기준치 미만일 경우 즉시 격리 조치를 취해야 한다...",
  "page_range": [3, 4],
  "citation": "SOP-QA-001, 4.2 (p.3-4)",
  "revision_date": "2025-01-15"
}
```

## 9. 결론

| 원칙 | 설명 |
|:---|:---|
| **의미 단위 청킹** | 페이지가 아닌 "조항/섹션" 단위로 청킹하여 맥락 보존 |
| **페이지 메타데이터** | 실제 인용 시 필요한 페이지 번호는 메타데이터로 저장 |
| **문서 유형별 프리셋** | SOP, 규정, BMR 등 유형에 맞는 전략 자동 적용 |
| **정규식 기반 분할** | 패턴 매칭으로 자동 분할 |

> **한 줄 요약:**
> **"SOP는 조항으로, 규정은 조문으로, 기록서는 페이지로 — 각각 최적의 칼로 자른다."**
