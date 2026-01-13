"""
Lecture Parser - DOCX/MD → Sections

Usage:
    from modules.lecture_parser import LectureParser
    
    parser = LectureParser()
    lecture = parser.parse("input/lecture.md")
    
    print(lecture.title)        # "7강. 인격적인 삶의 근거"
    print(len(lecture.sections)) # 4
    print(lecture.sections[0].title)  # "서론"
    print(lecture.sections[0].content)  # "오늘 우리는..."
"""
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Section:
    """강의 섹션"""
    number: int
    title: str
    content: str
    
    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Section({self.number}. {self.title}: {preview})"


@dataclass
class Lecture:
    """강의 전체"""
    title: str
    sections: List[Section] = field(default_factory=list)
    raw_content: str = ""
    
    def __repr__(self):
        return f"Lecture({self.title}, {len(self.sections)} sections)"


class LectureParser:
    """강의안 파서 (MD/DOCX)"""
    
    # 섹션 패턴: "1. 서론" 또는 "1. 서론\n" 형태
    SECTION_PATTERN = re.compile(
        r'^(\d+)\.\s+(.+?)(?:\r?\n|\r)',
        re.MULTILINE
    )
    
    def parse(self, file_path: str) -> Lecture:
        """파일 파싱"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == ".md":
            return self._parse_md(path)
        elif suffix == ".docx":
            return self._parse_docx(path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _parse_md(self, path: Path) -> Lecture:
        """마크다운 파싱"""
        content = path.read_text(encoding="utf-8")
        return self._parse_content(content)
    
    def _parse_docx(self, path: Path) -> Lecture:
        """DOCX 파싱"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx required. Install: pip install python-docx")
        
        doc = Document(path)
        content = "\n".join(para.text for para in doc.paragraphs)
        return self._parse_content(content)
    
    def _parse_content(self, content: str) -> Lecture:
        """내용 파싱 - 섹션 분리"""
        lines = content.strip().split("\n")
        
        # 첫 줄 = 강의 제목
        title = lines[0].strip() if lines else "Untitled"
        
        # 섹션 찾기 - 번호 패턴 먼저 시도
        sections = []
        matches = list(self.SECTION_PATTERN.finditer(content))
        
        if matches:
            # 번호가 있는 패턴 (1. 서론)
            for i, match in enumerate(matches):
                section_num = int(match.group(1))
                section_title = match.group(2).strip()
                
                start = match.end()
                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    end = len(content)
                
                section_content = content[start:end].strip()
                section_content = self._normalize_content(section_content)
                
                sections.append(Section(
                    number=section_num,
                    title=section_title,
                    content=section_content
                ))
        else:
            # 번호 없는 헤딩 패턴 (짧은 줄을 섹션 헤더로 간주)
            sections = self._parse_heading_style(content, title)
        
        return Lecture(
            title=title,
            sections=sections,
            raw_content=content
        )
    
    def _parse_heading_style(self, content: str, lecture_title: str) -> List[Section]:
        """헤딩 스타일 파싱 (DOCX용)"""
        lines = content.split("\n")
        sections = []
        current_section = None
        current_content = []
        section_num = 0
        
        # 헤딩으로 보이는 패턴: 짧은 줄 (5-40자), 다음 줄이 비었거나 긴 문장
        skip_keywords = [lecture_title, ":", "~", "–", "—"]
        
        for i, line in enumerate(lines):
            line_text = line.strip()
            
            # 빈 줄 스킵
            if not line_text:
                if current_section:
                    current_content.append("")
                continue
            
            # 강의 제목 등 메타 정보 스킵
            if i < 5 and (lecture_title in line_text or len(line_text) < 5):
                continue
            
            # 헤딩 후보: 짧은 줄 (5-40자), 한 줄짜리
            is_heading = (
                5 <= len(line_text) <= 40 and
                not line_text.endswith(('.', '?', '!', '니다', '습니다', '입니다')) and
                not any(c in line_text for c in ['(', ')', '"', "'"])
            )
            
            if is_heading and (line_text == "서론" or line_text.startswith("피히테") or 
                              ":" not in line_text[:10] or section_num == 0):
                # 새 섹션 시작
                if current_section and current_content:
                    sections.append(Section(
                        number=section_num,
                        title=current_section,
                        content=self._normalize_content("\n".join(current_content))
                    ))
                
                section_num += 1
                current_section = line_text
                current_content = []
            else:
                if current_section:
                    current_content.append(line_text)
        
        # 마지막 섹션 추가
        if current_section and current_content:
            sections.append(Section(
                number=section_num,
                title=current_section,
                content=self._normalize_content("\n".join(current_content))
            ))
        
        return sections
    
    def _normalize_content(self, content: str) -> str:
        """내용 정규화"""
        # 연속된 빈 줄을 하나로
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 줄 끝 공백 제거
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        return content.strip()


def main():
    """테스트"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lecture_parser.py <file.md|file.docx>")
        sys.exit(1)
    
    parser = LectureParser()
    lecture = parser.parse(sys.argv[1])
    
    print(f"📚 {lecture.title}")
    print(f"   섹션 수: {len(lecture.sections)}")
    print()
    
    for section in lecture.sections:
        print(f"{section.number}. {section.title}")
        print(f"   내용 길이: {len(section.content)} 자")
        print(f"   미리보기: {section.content[:100]}...")
        print()


if __name__ == "__main__":
    main()
