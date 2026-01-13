#!/usr/bin/env python3
"""
Phase 1.5: Academic Depth Enhancement Session
학술 깊이 강화 모듈 - Deep Research 출력의 약한 섹션을 선별적으로 심화

Usage:
    python depth_enhance_session.py <profile> <topic>
    Example: python depth_enhance_session.py account1 schechina
"""

import asyncio
import re
import sys
import subprocess
from dataclasses import dataclass
from pathlib import Path
from playwright.async_api import async_playwright


@dataclass
class Section:
    """리포트 섹션"""
    heading: str
    level: int  # ## = 2, ### = 3
    content: str
    start_line: int
    end_line: int
    score: float = 0.0


class DepthEnhanceSession:
    """학술 깊이 강화 세션"""
    
    # 학술 깊이 측정 지표
    SCHOLAR_PATTERN = r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s*\(\d{4}\)'  # "Moltmann (2001)"
    PRIMARY_PATTERNS = [
        r'\d+:\d+',  # 성경 구절 (예: 1:14)
        r'[α-ωΑ-Ω]+',  # 그리스어
        r'[\u0590-\u05FF]+',  # 히브리어
    ]
    TECHNICAL_PATTERN = r'\*[^*]+\*|\([A-Za-zäöüÄÖÜß]+\)'  # 이탤릭 또는 원어 괄호
    CONNECTOR_WORDS = ['그러나', '반면', '한편', '따라서', '이에 반해', '특히', '오히려', 'However', 'Nevertheless']
    COUNTER_KEYWORDS = ['비판', '한계', '반론', '반대', '문제점', 'critique', 'limitation', 'objection']
    
    PROFILES_DIR = Path(__file__).parent / ".profiles"
    
    def __init__(self, profile: str, topic: str):
        self.profile = profile
        self.topic = topic
        self.report_path = Path(f"reports/{topic}_raw.md")
        self.output_path = Path(f"reports/{topic}_enhanced.md")
        self.prompt_path = Path("prompts/depth_enhance_prompt.md")
        self.sections: list[Section] = []
        
        # 브라우저 프로필 디렉토리
        self.user_data_dir = self.PROFILES_DIR / profile
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_report(self) -> str:
        """리포트 로드"""
        if not self.report_path.exists():
            raise FileNotFoundError(f"리포트 없음: {self.report_path}")
        return self.report_path.read_text(encoding='utf-8')
    
    def parse_sections(self, content: str) -> list[Section]:
        """## 헤딩 기준으로 섹션 분리"""
        lines = content.split('\n')
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            # ## 또는 ### 헤딩 감지
            match = re.match(r'^(#{2,3})\s+(.+)$', line)
            if match:
                # 이전 섹션 저장
                if current_section:
                    current_section.end_line = i - 1
                    sections.append(current_section)
                
                level = len(match.group(1))
                heading = match.group(2).strip()
                current_section = Section(
                    heading=heading,
                    level=level,
                    content='',
                    start_line=i,
                    end_line=i
                )
            elif current_section:
                current_section.content += line + '\n'
        
        # 마지막 섹션 저장
        if current_section:
            current_section.end_line = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def score_section(self, section: Section) -> float:
        """학술 깊이 점수 계산 (0-100)"""
        text = section.content
        word_count = len(text.split())
        
        if word_count < 50:  # 너무 짧은 섹션 제외
            return 100  # 점수 높게 -> 강화 대상에서 제외
        
        # 1. 학자 언급 밀도 (25%)
        scholars = len(re.findall(self.SCHOLAR_PATTERN, text))
        scholar_score = min(scholars / (word_count / 100) * 10, 25)
        
        # 2. 1차 자료 인용 (25%)
        primary_count = sum(len(re.findall(p, text)) for p in self.PRIMARY_PATTERNS)
        primary_score = min(primary_count / (word_count / 100) * 8, 25)
        
        # 3. 전문 용어 밀도 (20%)
        terms = len(re.findall(self.TECHNICAL_PATTERN, text))
        term_score = min(terms / (word_count / 100) * 5, 20)
        
        # 4. 논증 구조 점수 (15%)
        connector_count = sum(1 for w in self.CONNECTOR_WORDS if w in text)
        connector_score = min(connector_count * 3, 15)
        
        # 5. 반론 고려 (15%)
        has_counter = any(k in text for k in self.COUNTER_KEYWORDS)
        counter_score = 15 if has_counter else 0
        
        total = scholar_score + primary_score + term_score + connector_score + counter_score
        return round(total, 1)
    
    def identify_weak_sections(self, n: int = 3) -> list[Section]:
        """하위 n개 섹션 반환 (## 레벨만)"""
        # ## 레벨 섹션만 필터 (주요 섹션)
        main_sections = [s for s in self.sections if s.level == 2]
        
        # 점수 계산
        for section in main_sections:
            section.score = self.score_section(section)
        
        # 점수 순 정렬 (낮은 점수 = 약한 섹션)
        sorted_sections = sorted(main_sections, key=lambda s: s.score)
        
        return sorted_sections[:n]
    
    def determine_weakness_type(self, section: Section) -> str:
        """섹션의 주요 약점 유형 판단"""
        text = section.content
        word_count = len(text.split())
        
        scholars = len(re.findall(self.SCHOLAR_PATTERN, text))
        primary = sum(len(re.findall(p, text)) for p in self.PRIMARY_PATTERNS)
        connectors = sum(1 for w in self.CONNECTOR_WORDS if w in text)
        has_counter = any(k in text for k in self.COUNTER_KEYWORDS)
        
        # 점수 비교로 가장 약한 부분 판단
        scores = {
            'scholar': scholars / max(word_count / 100, 1),
            'primary': primary / max(word_count / 100, 1),
            'structure': connectors + (5 if has_counter else 0)
        }
        
        weakest = min(scores, key=scores.get)
        return weakest
    
    def generate_enhancement_prompt(self, section: Section) -> str:
        """섹션 유형에 맞는 심화 프롬프트 생성"""
        weakness = self.determine_weakness_type(section)
        
        base_prompt = f"## 섹션 심화 요청\n\n**섹션 제목**: {section.heading}\n\n"
        
        if weakness == 'scholar':
            prompt = base_prompt + """**개선 방향**: 학자 언급 강화

이 섹션을 다음 관점에서 확장하세요:

1. 이 주제의 **대표적 독일어권 학자 2-3명**과 그들의 핵심 주장
2. **영미권의 대응 논의** 1-2명
3. 학파 간 쟁점이 있다면 명시
4. 각 학자의 대표 저작(논문/단행본)과 출판 연도 포함

"""
        elif weakness == 'primary':
            prompt = base_prompt + """**개선 방향**: 1차 자료 강화

이 섹션에 다음을 추가하세요:

1. 관련 성경 본문의 **원어(헬라어/히브리어) 핵심 용어** 분석
2. 해당 용어의 **LXX/MT/NT 용례** 비교
3. 주요 **사전·주석서** 참조:
   - 어휘사전: ThWNT/TWNT, ThWAT/TWAT, EWNT, BDAG, HALOT, Gesenius, BDB
   - 백과사전: RGG(4판), TRE, HWPh, TDNT
   - 주석서: KEK, HThK, ATD, KAT, WBC, ICC, NIGTC
4. 필요시 **독일어 신학 용어**의 뉘앙스 설명

"""
        else:  # structure
            prompt = base_prompt + """**개선 방향**: 논증 구조 강화

이 섹션의 논증을 강화하세요:

1. **주장(thesis)**을 명확히 진술
2. **근거 1-2개**를 학술 문헌에서 인용
3. **가능한 반론**과 그에 대한 응답 포함
4. **결론**을 명시
5. 전환어("그러나", "한편", "이에 반해" 등) 활용

"""
        
        prompt += f"**기존 내용**:\n\n{section.content[:2000]}...\n\n---\n\n"
        prompt += "**지시사항**: 기존 내용을 대체하지 말고, 확장·심화하여 출력하세요. 헤딩(`##`)은 그대로 유지합니다."
        
        return prompt
    
    def build_full_prompt(self, weak_sections: list[Section]) -> str:
        """전체 심화 프롬프트 구축"""
        prompt = """# Phase 1.5: Academic Depth Enhancement

당신은 신학 학술 논문의 깊이 강화 전문가입니다.

아래 3개 섹션이 학술적 깊이가 부족합니다. 각 섹션을 지시에 따라 심화하세요.

## 핵심 규칙

1. **기존 구조 유지**: 헤딩(`##`, `###`)과 기존 내용을 보존
2. **확장 추가**: 지시된 방향으로 내용을 추가/확장
3. **학술 품질**: 학자명(연도), 원어, 전문 용어 적극 활용
4. **분량**: 각 섹션당 500-1000자 추가

---

"""
        
        for i, section in enumerate(weak_sections, 1):
            prompt += f"\n### 약점 섹션 {i} (점수: {section.score}/100)\n\n"
            prompt += self.generate_enhancement_prompt(section)
            prompt += "\n\n---\n"
        
        prompt += """

## ⚠️ 출력 형식

각 섹션별로 다음 형식으로 출력하세요:

```
## [섹션 제목]

[확장된 내용]
```

**프롬프트나 지시사항은 출력하지 마세요. 확장된 3개 섹션만 출력하세요.**
"""
        
        return prompt
    
    def merge_enhanced_sections(self, original: str, enhanced_text: str) -> str:
        """원본에 확장된 섹션 병합"""
        # 확장된 섹션들을 파싱
        enhanced_sections = re.findall(r'^##\s+(.+?)\n(.*?)(?=^##|\Z)', 
                                       enhanced_text, re.MULTILINE | re.DOTALL)
        
        result = original
        for heading, content in enhanced_sections:
            heading = heading.strip().replace('**', '').replace('\\', '')
            # 원본에서 해당 헤딩 찾기
            pattern = rf'(##\s+\**{re.escape(heading)}\**\n)(.*?)(?=\n##|\Z)'
            
            def replacer(match):
                original_heading = match.group(1)
                # 확장된 내용으로 대체
                return original_heading + content.strip() + '\n\n'
            
            result = re.sub(pattern, replacer, result, flags=re.DOTALL)
        
        return result
    
    async def run(self):
        """메인 실행"""
        print("=" * 60)
        print("  Phase 1.5: Academic Depth Enhancement")
        print("=" * 60)
        print()
        
        # 1. 리포트 로드
        print(f"📄 리포트 로드: {self.report_path}")
        content = self.load_report()
        print(f"   ✓ {len(content):,} 문자")
        
        # 2. 섹션 파싱
        self.sections = self.parse_sections(content)
        print(f"\n📊 섹션 분석: {len(self.sections)}개 섹션 감지")
        
        # 3. 약한 섹션 식별
        weak_sections = self.identify_weak_sections(3)
        print(f"\n⚠️  하위 섹션 (강화 대상):")
        for s in weak_sections:
            weakness = self.determine_weakness_type(s)
            print(f"   • {s.heading[:40]}... (점수: {s.score}, 약점: {weakness})")
        
        # 4. 프롬프트 생성
        prompt = self.build_full_prompt(weak_sections)
        print(f"\n📝 심화 프롬프트 생성: {len(prompt):,} 문자")
        
        # 5. 클립보드에 복사
        subprocess.run(['pbcopy'], input=prompt.encode('utf-8'))
        print("\n✅ 프롬프트가 클립보드에 복사되었습니다!")
        
        # 6. 브라우저 열기 (프로필 사용)
        print(f"\n🌐 브라우저 시작... (프로필: {self.profile})")
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = context.pages[0] if context.pages else await context.new_page()
            await page.goto('https://gemini.google.com/')
            
            print("""
┌──────────────────────────────────────────────────────────┐
│  PHASE 1.5: Academic Depth Enhancement                  │
└──────────────────────────────────────────────────────────┘

📝 작업 순서:
   1. Gemini에 프롬프트 붙여넣기 (Cmd+V)
   2. 전송 후 응답 대기
   3. 확장된 3개 섹션을 복사 (Cmd+A → Cmd+C)
   4. 터미널로 돌아와 Enter

💡 출력은 `## 섹션제목` 형식으로 시작해야 합니다!
""")
            
            input("⏳ 결과 복사 후 Enter를 눌러주세요...")
            
            await context.close()
        
        # 7. 클립보드에서 결과 읽기
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        enhanced_text = result.stdout
        
        if not enhanced_text.strip():
            print("❌ 클립보드가 비어있습니다!")
            return
        
        print(f"\n📋 확장 결과 수신: {len(enhanced_text):,} 문자")
        
        # 8. 병합 및 저장
        merged = self.merge_enhanced_sections(content, enhanced_text)
        self.output_path.write_text(merged, encoding='utf-8')
        
        print(f"""
============================================================
✅ Phase 1.5 완료!
============================================================
📄 출력 파일: {self.output_path}
📊 원본 크기: {len(content):,} 문자
📊 결과 크기: {len(merged):,} 문자
📈 증가량: +{len(merged) - len(content):,} 문자
""")


async def main():
    if len(sys.argv) < 3:
        print("Usage: python depth_enhance_session.py <profile> <topic>")
        print("Example: python depth_enhance_session.py account1 schechina")
        sys.exit(1)
    
    profile = sys.argv[1]
    topic = sys.argv[2]
    session = DepthEnhanceSession(profile, topic)
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
