"""
Outline Generator - Gemini API로 이중언어 개요 생성

Usage:
    from modules.outline_generator import OutlineGenerator
    from modules.lecture_parser import LectureParser
    
    parser = LectureParser()
    lecture = parser.parse("input/lecture.md")
    
    generator = OutlineGenerator()
    outline = generator.generate(lecture)
    
    for item in outline:
        print(item["ko"], item["en"])
"""
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GOOGLE_API_KEY, OUTLINE_MODEL


@dataclass
class OutlineItem:
    """개요 항목"""
    ko: str  # 한국어
    en: str  # 영어
    section_num: int = 0
    section_title: str = ""


class OutlineGenerator:
    """이중언어 개요 생성기"""
    
    SYSTEM_PROMPT = """당신은 신학 강의 슬라이드 개요 전문가입니다.
주어진 강의 섹션을 분석하여 시청자가 이해하기 쉬운 핵심 포인트를 추출합니다.

규칙:
1. 각 섹션당 3-5개의 핵심 포인트 추출
2. **시청자 친화적으로 작성**: 
   - 간결하되 문맥을 알 수 있게
   - 콜론(:) 또는 화살표(→)로 핵심 연결
   - ❌ 너무 짧음: "전능 재정의"
   - ❌ 너무 김: "신의 전능함을 논리적 한계 내에서 재정의하여 악의 문제를 해결합니다."
   - ✅ 적절함: "전능 재정의: 논리적 한계 내 신적 능력"
3. 한국어 25-40자 내외 (읽기 편한 길이)
4. 영어는 한국어의 정확한 번역
5. JSON 형식으로 출력

출력 형식:
{
    "section_title": "섹션 제목",
    "section_title_en": "Section Title",
    "points": [
        {"ko": "핵심 개념: 구체적 설명", "en": "Key Concept: specific explanation"},
        {"ko": "주요 논점: 이해하기 쉬운 내용", "en": "Main Point: accessible content"}
    ]
}
"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GOOGLE_API_KEY
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of GenAI client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not set. Check .env file.")
            
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        
        return self._client
    
    def generate(self, lecture) -> List[Dict]:
        """전체 강의 개요 생성"""
        all_outlines = []
        
        for section in lecture.sections:
            outline = self.generate_section_outline(section)
            all_outlines.append(outline)
        
        return all_outlines
    
    def generate_section_outline(self, section) -> Dict:
        """섹션별 개요 생성"""
        from google.genai import types
        
        prompt = f"""다음 강의 섹션의 개요를 생성하세요.

섹션 번호: {section.number}
섹션 제목: {section.title}
섹션 내용:
{section.content[:3000]}  # 토큰 제한을 위해 잘라냄

위 내용을 분석하여 JSON 형식으로 개요를 생성하세요.
"""
        
        response = self.client.models.generate_content(
            model=OUTLINE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM_PROMPT,
                temperature=0.3
            )
        )
        
        # JSON 파싱
        try:
            text = response.text
            # JSON 블록 추출
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            outline = json.loads(text.strip())
            outline["section_num"] = section.number
            return outline
        except json.JSONDecodeError:
            # 파싱 실패 시 기본 구조 반환
            return {
                "section_num": section.number,
                "section_title": section.title,
                "section_title_en": section.title,
                "points": [
                    {"ko": section.title, "en": section.title}
                ],
                "raw_response": response.text
            }
    
    def save_outline(self, outlines: List[Dict], output_path: str):
        """개요 JSON 저장"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(outlines, f, ensure_ascii=False, indent=2)


def main():
    """테스트"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from modules.lecture_parser import LectureParser
    
    if len(sys.argv) < 2:
        print("Usage: python outline_generator.py <lecture.md>")
        sys.exit(1)
    
    parser = LectureParser()
    lecture = parser.parse(sys.argv[1])
    
    print(f"📚 {lecture.title}")
    print(f"   섹션 수: {len(lecture.sections)}")
    print()
    
    generator = OutlineGenerator()
    
    for section in lecture.sections:
        print(f"🔄 섹션 {section.number}: {section.title}")
        outline = generator.generate_section_outline(section)
        
        print(f"   📝 제목: {outline.get('section_title', section.title)}")
        print(f"   📝 Title: {outline.get('section_title_en', '')}")
        
        for i, point in enumerate(outline.get("points", []), 1):
            print(f"   {i}. {point.get('ko', '')}")
            print(f"      {point.get('en', '')}")
        print()


if __name__ == "__main__":
    main()
