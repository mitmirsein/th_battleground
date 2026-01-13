"""
Slide Generator - 개요 → SVG → PNG 슬라이드 생성

Usage:
    from modules.slide_generator import SlideGenerator
    
    generator = SlideGenerator()
    slides = generator.generate(outlines, lecture_title="7강. 인격적인 삶의 근거")
    generator.save_slides(slides, "output/")
"""
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    SLIDE_WIDTH, SLIDE_HEIGHT, COLORS, FONTS,
    TEMPLATES_DIR, OUTPUT_DIR
)


@dataclass
class Slide:
    """슬라이드"""
    number: int
    svg_content: str
    lecture_title: str = ""
    section_title_ko: str = ""
    section_title_en: str = ""
    points: List[Dict] = None


class SlideGenerator:
    """SVG 슬라이드 생성기"""
    
    def __init__(self):
        self.width = SLIDE_WIDTH
        self.height = SLIDE_HEIGHT
        self.colors = COLORS
        self.fonts = FONTS
    
    def generate(self, outlines: List[Dict], lecture_title: str = "") -> List[Slide]:
        """전체 슬라이드 생성"""
        slides = []
        total_slides = len(outlines)
        
        for i, outline in enumerate(outlines, 1):
            slide = self._generate_slide(
                outline=outline,
                slide_num=i,
                total_slides=total_slides,
                lecture_title=lecture_title
            )
            slides.append(slide)
        
        return slides
    
    def _generate_slide(
        self,
        outline: Dict,
        slide_num: int,
        total_slides: int,
        lecture_title: str
    ) -> Slide:
        """단일 슬라이드 생성"""
        section_title_ko = outline.get("section_title", "")
        section_title_en = outline.get("section_title_en", "")
        points = outline.get("points", [])
        
        svg = self._render_svg(
            lecture_title=lecture_title,
            section_title_ko=section_title_ko,
            section_title_en=section_title_en,
            points=points,
            slide_num=slide_num,
            total_slides=total_slides
        )
        
        return Slide(
            number=slide_num,
            svg_content=svg,
            lecture_title=lecture_title,
            section_title_ko=section_title_ko,
            section_title_en=section_title_en,
            points=points
        )
    
    def _render_svg(
        self,
        lecture_title: str,
        section_title_ko: str,
        section_title_en: str,
        points: List[Dict],
        slide_num: int,
        total_slides: int
    ) -> str:
        """SVG 렌더링"""
    def _render_svg(
        self,
        lecture_title: str,
        section_title_ko: str,
        section_title_en: str,
        points: List[Dict],
        slide_num: int,
        total_slides: int
    ) -> str:
        """SVG 렌더링 (Premium Design)"""
        
        # 포인트 텍스트 생성
        points_svg = ""
        # 그룹 시작 위치 (translate(150, 380))
        # 내부 좌표는 0,0 기준
        y_offset = 0
        max_points = 4  # 최대 포인트 수 제한 (디자인상 공간 확보)
        
        for i, point in enumerate(points[:max_points]):
            label = point.get("ko", "").split(":")[0] if ":" in point.get("ko", "") else f"Point {i+1}"
            content_ko = point.get("ko", "")
            # 레이블이 내용에 포함되어 있으면 제거 (중복 방지)
            if label in content_ko:
                content_ko = content_ko.replace(f"{label}:", "").strip()
            
            content_en = point.get("en", "")
            
            label = self._escape_xml(self._truncate_text(label, 15))
            content_ko = self._escape_xml(self._truncate_text(content_ko, 50))
            content_en = self._escape_xml(content_en)
            
            points_svg += f'''
    <!-- Point {i+1} -->
    <text x="0" y="{y_offset}" font-family="{self.fonts['body']}" font-size="30" font-weight="bold" fill="{self.colors['accent']}">{label}</text>
    <text x="250" y="{y_offset}" font-family="{self.fonts['body']}" font-size="28" fill="{self.colors['text_main']}">{content_ko}</text>
    <text x="250" y="{y_offset + 35}" font-family="{self.fonts['body']}" font-size="20" fill="{self.colors['text_sub']}" font-style="italic">{content_en}</text>
'''
            y_offset += 110  # 간격 110px
        
        # 타이틀 강조 처리 (첫 단어만 강조하거나 전체 강조)
        # 예시처럼 특정 단어 강조는 NLP 필요하므로 여기선 전체 타이틀 적용
        # 대신 <tspan>으로 색상 적용 가능하도록 구조 유지
        
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{self.colors['bg_start']};stop-opacity:1" />
      <stop offset="70%" style="stop-color:{self.colors['bg_mid']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{self.colors['bg_end']};stop-opacity:1" />
    </linearGradient>
    <pattern id="pattern1" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
      <circle cx="50" cy="50" r="1" fill="{self.colors['pattern']}" opacity="0.25"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="100%" height="100%" fill="url(#grad1)" />
  <rect width="100%" height="100%" fill="url(#pattern1)" />
  
  <!-- Title Area -->
  <text x="150" y="120" font-family="{self.fonts['body']}" font-size="32" font-weight="normal" fill="{self.colors['text_sub']}">
    {self._escape_xml(lecture_title)}
  </text>
  
  <text x="150" y="190" font-family="{self.fonts['title']}" font-size="52" font-weight="bold" fill="{self.colors['title']}">
    {self._escape_xml(section_title_ko)}
  </text>
  
  <text x="150" y="240" font-family="{self.fonts['body']}" font-size="30" font-weight="normal" fill="{self.colors['text_sub']}">
    {self._escape_xml(section_title_en)}
  </text>
  
  <line x1="150" y1="270" x2="850" y2="270" stroke="{self.colors['accent']}" stroke-width="3"/>
  
  <!-- Content Area -->
  <g transform="translate(150, 380)">
    {points_svg}
  </g>
  
  <!-- Page Number -->
  <text x="1800" y="1040" font-family="{self.fonts['body']}" font-size="24" fill="#FFFFFF" opacity="0.7" text-anchor="middle">{slide_num} / {total_slides}</text>
</svg>'''
        
        return svg
    
    def _truncate_text(self, text: str, max_chars: int = 50) -> str:
        """텍스트 길이 제한 (말줄임표 추가)"""
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 1] + "…"
    
    def _escape_xml(self, text: str) -> str:
        """XML 특수문자 이스케이프"""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))
    
    def save_slides(self, slides: List[Slide], output_dir: str = None) -> List[str]:
        """슬라이드 저장 (SVG + PNG)"""
        output_path = Path(output_dir or OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)
        
        saved_files = []
        
        for slide in slides:
            # SVG 저장
            svg_file = output_path / f"slide_{slide.number:02d}.svg"
            svg_file.write_text(slide.svg_content, encoding="utf-8")
            saved_files.append(str(svg_file))
            
            # PNG 변환
            png_file = output_path / f"slide_{slide.number:02d}.png"
            self._svg_to_png(str(svg_file), str(png_file))
            saved_files.append(str(png_file))
        
        return saved_files
    
    def _svg_to_png(self, svg_path: str, png_path: str):
        """SVG → PNG 변환"""
        try:
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path)
        except ImportError:
            print("⚠️ cairosvg not installed. PNG conversion skipped.")
            print("   Install: pip install cairosvg")


def main():
    """테스트"""
    # 샘플 개요 데이터
    sample_outlines = [
        {
            "section_title": "서론",
            "section_title_en": "Introduction",
            "points": [
                {"ko": "인격적인 삶의 근거로서의 신을 재탐색", "en": "Reexploring God as the foundation of personal life"},
                {"ko": "전통적 전능함 개념의 문제점 분석", "en": "Analyzing problems with traditional omnipotence"},
                {"ko": "이성과 논리로 신의 본질 정립", "en": "Establishing God's essence through reason and logic"},
            ]
        },
        {
            "section_title": "신의 전능함에 대한 이성적인 해체와 재구성",
            "section_title_en": "Rational Deconstruction and Reconstruction of Divine Omnipotence",
            "points": [
                {"ko": "스윈번의 전능함 재정의", "en": "Swinburne's redefinition of omnipotence"},
                {"ko": "논리적 제약 안에서의 신적 능력", "en": "Divine power within logical constraints"},
            ]
        }
    ]
    
    generator = SlideGenerator()
    slides = generator.generate(sample_outlines, lecture_title="7강. 인격적인 삶의 근거")
    
    print(f"📊 생성된 슬라이드: {len(slides)}개")
    
    saved = generator.save_slides(slides, "output/test_slides")
    print(f"💾 저장된 파일: {len(saved)}개")
    for f in saved:
        print(f"   - {f}")


if __name__ == "__main__":
    main()
