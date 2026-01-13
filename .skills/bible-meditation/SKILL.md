---
name: Bible Meditation Protocol
description: Standard ARC protocol for processing daily bible meditations (Analysis -> Dialogue -> Article -> TTS -> Translation).
version: 1.0.0
---

# Bible Meditation Protocol

## 1. Description
이 스킬은 사용자의 초기 묵상 노트(Raw Note)를 바탕으로 심도 있는 신학적 아티클, 적용점, TTS 대본, 그리고 영문 번역본을 순차적으로 생성합니다.

## 2. Trigger
- 사용자가 "묵상 프로토콜 실행해줘", "이 묵상 발전시켜줘"라고 요청할 때.
- 사용자가 `/arc` 명령어를 입력하고 해당 파일이 묵상 노트일 때.

## 3. Workflow Steps (Must Follow Sequentially)

### Phase 1: Analysis & Dialogue (분석 및 대화)
1.  **Read**: 현재 활성화된 문서(Active Document)를 읽으십시오.
2.  **Analyze**: 핵심 구절, 직관적 통찰, 주요 키워드를 파악하십시오.
3.  **Question**: 묵상을 심화시키기 위한 '신학적 질문' 1~2가지를 생성하여 사용자에게 제시하십시오.
4.  **🛑 STOP**: 질문을 던진 후에는 반드시 멈추고 사용자의 답변을 기다리십시오.

### Phase 2: Synthesis & Drafting (종합 및 초안 작성)
*Trigger: 사용자가 질문에 답변하면 시작*
1.  **Protocol**: 사용자의 답변을 요약하여 문서 본문에 `### 💬 신학적 대화 프로토콜` 섹션을 추가하십시오.
2.  **Drafting**: 다음 3가지 요소를 작성하여 문서 하단에 추가하십시오.
    - **Main Article**: 감동적인 제목, 핵심 구절, 2-3문단의 신학적 에세이.
    - **Devotional**: `### 📖 묵상 (YYYY. MM. DD.)`, 한 줄 요약, 적용, 기도.
    - **TTS Script**: `%%TTS-SCRIPT:` 블록, 라디오 오프닝 스타일.
3.  **🛑 STOP**: "초안이 작성되었습니다. 내용을 검토해주세요."라고 말하고 멈추십시오.

### Phase 3: Translation (번역)
*Trigger: 사용자가 "교정 완료" 또는 "번역해줘"라고 하면 시작*
1.  **Read**: 사용자가 수정한(교정한) 문서를 다시 읽으십시오.
2.  **Translate**: 'Main Article' 섹션만 영문으로 번역하십시오. (N.T. Wright/C.S. Lewis 스타일)
3.  **Append**: 문서 최하단에 `### **[English Title]**`과 함께 번역문을 추가하십시오.
4.  **Finish**: 완료 메시지를 출력하고 종료하십시오.

## 4. Rules
- **파일 수정**: `multi_replace_file_content` 또는 `replace_file_content`를 사용하여 한 번에 깔끔하게 추가하십시오.
- **톤 앤 매너**: 신학적으로 깊이 있으면서도 문학적인 우아함을 유지하십시오.
