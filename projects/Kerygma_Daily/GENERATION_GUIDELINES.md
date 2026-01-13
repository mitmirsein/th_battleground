# ‘케리그마 매일 묵상’ 생성 지침 (Kerygma Daily Meditation Generation Guidelines)

이 문서는 프로젝트 작업 시 모든 참여자(AI 및 작업자)가 준수해야 할 생성 원칙을 정의합니다.

## 1. Core Principle (핵심 원칙)
> **Think faithful, smart, and hard.**
> (신실하게, 지혜롭게, 그리고 치열하게 고민하라.)

## 2. Text Selection (본문 선정)
- **Selection Criteria**: 매일의 RCL(Revised Common Lectionary) 본문 중, **구약에서 핵심 1구절**, **신약에서 핵심 1구절**을 선정한다. (가장 중요한 단계)
- **Emphasis**: 선입견이나 전이해(Pre-understanding)를 경계하고, **RCL이 제시하는 본문 자체에 집중**하여 그 구절들로부터 핵심을 도출한다.
- **Scope**: 작업은 **한 주간 단위(일요일~토요일)**로 진행한다.

## 3. Content Requirements (내용 필수 사항)
- **Original Languages**: 선정된 구절의 **원어 본문 전체**를 반드시 표기해야 한다.
  - **OT (구약)**: 히브리어 (Hebrew)
  - **NT (신약)**: 헬라어 (Greek)
  - **Word Parsing**: 각 단어는 `text`, `sound`(음역), `lemma`(기본형), `lemma_sound`(기본형 음역), `morph`, `gloss`를 포함해야 한다. (기본형 음역 필수)
- **Literal Translation (직역 원칙)**:
  - **Completeness**: `focus_text`(원어 본문)로 선정된 범위는 **빠짐없이** 직역(`kor_lit`)에 포함되어야 한다. 문장이 길더라도 절대 임의로 생략하거나 축약하지 않는다.
  - **Match**: `kor_lit`의 범위는 `focus_text`의 범위와 정확히 일치해야 한다.
  - **Format**: `한글 의미(원어 음역)` 순서로 작성한다. (예: `처녀가 기뻐할 것이다(티세마흐 베툴라)`)

## 4. Meditation Generation Guidelines (오늘의 묵상 생성 지침)
- **Intent (의도)**: 독자 친화적(Reader-Friendly)으로 작성한다. **위로, 격려, 희망, 평안의 메시지를 전하려는 의도**를 가장 우선한다.
- **Connection (연관성)**: 묵상 내용은 선정된 **구약 본문과 신약 본문의 메시지를 유기적으로 연결**해야 한다. 두 텍스트가 어떻게 서로를 조명하는지 드러내야 한다.
- **Ending (마무리)**: 묵상글의 마지막 문장은 반드시 독자에게 **위로, 평안, 희망, 힘을 주는 문장**으로 마무리해야 한다.
- **Question (성찰 질문)**:
  - **Avoid**: 양자택일형 질문("~입니까, 아니면 ~입니까?"), 감정을 부추기거나 부정적인 상태를 전제하는 질문("슬픔에 잠겨 있습니까?").
  - **Pursue**: 주님의 은혜, 사랑, 능력이 필요한 영역을 묻는 건설적이고 부드러운 질문("어느 부분에 주님의 은혜가 필요합니까?"). 위로와 격려의 톤 유지.
- **Language (용어 사용)**:
  - 묵상 본문에 원어를 인용할 경우, 반드시 **한글 의미('원어 음역')** 순서로 작성한다. (예: `일어나 빛을 발하라('쿠미 오리')`)

---
*Created: 2026-01-03*
