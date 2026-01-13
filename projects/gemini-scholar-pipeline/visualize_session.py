#!/usr/bin/env python3
"""
Phase 6: Report Visualization
Markdown → Interactive HTML 변환 모듈

Usage:
    python visualize_session.py --topic {topic} [--mode full|condensed|both]
    
Input:
    - reports/{topic}_final.md (또는 _annotated.md)
    - reports/{topic}_footnotes.json
    
Output:
    - reports/{topic}_report.html (full 모드)
    - reports/{topic}_brief.html (condensed 모드)
"""

import argparse
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import markdown


class Section:
    """섹션 데이터 클래스"""
    def __init__(self, title: str, content: str, level: int = 2,
                 essence: str = "", keywords: list = None):
        self.title = title
        self.nav_title = title[:12] + "..." if len(title) > 15 else title
        self.content = content
        self.level = level
        self.essence = essence
        self.keywords = keywords or []


class Footnote:
    """각주 데이터 클래스"""
    def __init__(self, id: int, citation: str):
        self.id = id
        self.citation = citation


def extract_essence_and_keywords(content: str) -> tuple[str, list[str]]:
    """
    섹션 콘텐츠에서 essence(핵심 문장)와 keywords 추출
    
    - essence: 첫 번째 의미 있는 문장 (하위 섹션 헤딩 제외)
    - keywords: 대문자로 시작하는 키워드, 인용문, 주요 용어
    """
    # Essence 추출 개선
    # 1. 헤딩(h3~h6), 리스트(ul, ol), 테이블(table) 태그가 나오기 전까지만 텍스트 추출 (Intro)
    split_pattern = re.compile(r'<(h[3-6]|ul|ol|table)', re.IGNORECASE)
    parts = split_pattern.split(content, 1)
    
    intro_html = parts[0]
    
    # 2. 태그 제거 및 텍스트 정제
    text = re.sub(r'<[^>]+>', '', intro_html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fallback: Intro가 너무 짧으면(30자 미만) 뒷부분(parts[2]) 텍스트도 가져옴
    if len(text) < 30 and len(parts) > 2:
        # parts[1]은 매칭된 태그이므로 제외하고 parts[2](그 이후 내용) 사용
        body_text = re.sub(r'<[^>]+>', '', parts[2])
        body_text = re.sub(r'\s+', ' ', body_text).strip()
        text += " " + body_text
    
    # 3. 문장 분리
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    essence = ""
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        # 건너뛸 패턴들
        if re.match(r'^\d+\.?\s*$', sentence): continue
        if len(sentence) < 5: continue # 너무 짧은 건 무시
        
        # 300자 제한 체크
        if current_length + len(sentence) > 300:
            # 첫 문장인데 300자 넘으면 잘라서라도 넣음
            if current_length == 0:
                essence = sentence
            break
            
        essence += sentence + " "
        current_length += len(sentence) + 1
    
    essence = essence.strip()
    
    # 너무 길면 마침표/쉼표 위치에서 자르기 (최대 300자 + 여유)
    if len(essence) > 300:
        # 마침표 위치 찾기
        cut_pos = essence.rfind('.', 0, 300)
        if cut_pos == -1:
            cut_pos = essence.rfind(',', 0, 300)
        
        if cut_pos > 50:
            essence = essence[:cut_pos + 1]
        else:
            essence = essence[:297] + "..."
            
    # Keywords 추출 (전체 content에서)
    keywords = []
    
    # 1. 영어 대문자 단어 (학술 용어)
    caps_words = re.findall(r'\b([A-Z][a-zA-Z]{2,})\b', content)
    for word in caps_words[:5]:
        if word not in ['The', 'This', 'That', 'These', 'Those', 'There']:
            keywords.append(word)
    
    # 2. 괄호 안 원어 (예: 셰키나(Schechina))
    foreign_terms = re.findall(r'\(([A-Za-z]+)\)', content)
    keywords.extend(foreign_terms[:3])
    
    # 중복 제거 및 최대 5개
    keywords = list(dict.fromkeys(keywords))[:5]
    
    return essence, keywords


def parse_markdown_sections(md_content: str, extract_extras: bool = False) -> tuple[list[Section], str, str]:
    """
    마크다운을 섹션별로 파싱
    
    두 가지 섹션 패턴 지원:
    1. ## **1\. 서론...** (H2 형식)
    2. **2\. 어원적...** (Bold 텍스트 형식)
    
    개선사항:
    - 코드 블록 (```markdown) 내부 본문 추출
    - escaped 문자 (\*\*, \\.) 정리
    - 하위 섹션 (###) 콘텐츠로 병합
    
    Args:
        extract_extras: True면 essence와 keywords도 추출 (condensed 모드용)
    
    Returns:
        (sections, subtitle, abstract)
    """
    # 1. 전처리: 코드 블록 내부 본문 추출
    # ```markdown ... ``` 패턴 검색
    code_block_pattern = re.compile(r'```(?:markdown|md)?\s*\n(.*?)```', re.DOTALL)
    code_blocks = code_block_pattern.findall(md_content)
    if code_blocks:
        # 첫 번째 코드 블록(Main Article)만 사용
        # Deliverable 2, 3 등은 제외
        md_content = code_blocks[0]
    
    # 2. 전처리: escaped 문자 정리
    md_content = md_content.replace('\\*\\*', '**')
    md_content = md_content.replace('\\.', '.')
    md_content = md_content.replace('\\-', '-')
    
    lines = md_content.split('\n')
    sections = []
    current_section = None
    current_content = []
    
    # 필터링할 메타 섹션들 (Brief에서 제외)
    META_SECTIONS = ['endnotes', 'bibliography', 'source comparison', 'references', 
                     '참고 문헌', '참고문헌', '참고 자료', 'endnote', 
                     'deliverable', 'source ledger', 'method',
                     'abstract', '초록']
    
    # 첫 번째 섹션 전 내용 (abstract로 사용)
    abstract_lines = []
    abstract = ""
    found_first_section = False
    subtitle = ""
    skip_current_section = False
    
    # 메인 섹션 패턴 (## 로 시작하는 H2 헤딩만)
    # ### 하위 섹션은 콘텐츠로 포함
    
    for line in lines:
        # H1 제목 건너뛰기 (타이틀로 사용됨)
        if line.startswith('# ') and not line.startswith('## '):
            continue
        
        # --- 구분선은 무시
        if line.strip() == '## ---' or line.strip() == '---' or line.strip() == '-----':
            continue
        
        # H2 섹션 감지: ## 로 시작하는 라인만 새 섹션
        if line.startswith('## '):
            section_title = line[3:].strip()
            
            # 메타 섹션 필터링
            is_meta = any(meta in section_title.lower() for meta in META_SECTIONS)
            if is_meta:
                skip_current_section = True
                continue
            
            # 제목 정리
            clean_title = section_title
            skipping_subsection = False # 새 메인 섹션 시작 시 리셋
            
            # 이전 섹션 저장
            if current_section and not skip_current_section:
                content_md = '\n'.join(current_content)
                # Apply Citation Styling
                content_md = re.sub(r'\(Source: \[?([a-zA-Z0-9]+)\]?\)', 
                      r'<span class="citation-source text-accent-teal font-mono font-bold text-xs cursor-help" title="Source ID: \1">[SRC:\1]</span>', 
                      content_md)
                      
                content_html = markdown.markdown(content_md, extensions=['tables', 'fenced_code'])
                
                # Abstract 섹션 체크
                if any(x in current_section.lower() for x in ['abstract', '초록']):
                     # Clipboard content는 보통 전체 내용을 담고 있을 수 있으나, 여기서는 섹션명으로 걸러냄
                     if any(x in current_section.lower() for x in ['abstract', '초록']):
                        abstract = md_to_inline_html(content_md)
                # 메타 섹션 필터링 (부분 일치 허용)
                elif not any(meta in current_section.lower() for meta in META_SECTIONS):
                    if extract_extras:
                        essence, keywords = extract_essence_and_keywords(content_html)
                        # essence가 비어있으면 content의 첫 500자를 사용
                        if not essence:
                            essence = content_html[:500].split('</p>')[0].replace('<p>', '').strip() + "..." if len(content_html) > 500 else content_html.strip()
                        sections.append(Section(current_section, content_html, 
                                              essence=essence, keywords=keywords))
                    else:
                        sections.append(Section(current_section, content_html))
            
            # 빈 제목이면 건너뛰기
            if not clean_title or clean_title == '---':
                continue
            
            # 새 섹션 시작
            current_section = clean_title
            current_content = []
            
            # 새 섹션이 메타 섹션인지 확인 (H2 레벨)
            skip_current_section = False
            if any(meta in current_section.lower() for meta in META_SECTIONS):
                 skip_current_section = True
            
            found_first_section = True
            
        elif line.startswith('###') or line.startswith('####'):
            # 하위 섹션이 메타 섹션인지 확인
            if any(meta in clean_title.lower() for meta in META_SECTIONS):
                skipping_subsection = True
            else:
                skipping_subsection = False
                if found_first_section and current_section and not skip_current_section:
                    current_content.append(line)
        
        elif found_first_section and current_section and not skip_current_section and not skipping_subsection:
            # H3, H4 서브섹션 및 모든 콘텐츠를 현재 섹션에 포함
            current_content.append(line)
        elif not found_first_section:
            # 첫 섹션 전 내용 수집 (abstract 후보)
            # YAML frontmatter 및 메타데이터 건너뛰기
            if line.strip() and not line.startswith('---') and not line.startswith('title:') and not line.startswith('generated:') and not line.startswith('source:') and not line.startswith('phase:') and not line.startswith('**분류**') and not line.startswith('**언어**'):
                abstract_lines.append(line)
    
    # 코드 블록 내부의 #, ## 는 무시해야 함
    # 마지막 섹션 저장
    if current_section and not skip_current_section:
        content_md = '\n'.join(current_content)
        # Apply Citation Styling
        content_md = re.sub(r'\(Source: \[?([a-zA-Z0-9]+)\]?\)', 
              r'<span class="citation-source text-accent-teal font-mono font-bold text-xs cursor-help" title="Source ID: \1">[SRC:\1]</span>', 
              content_md)

        content_html = markdown.markdown(content_md, extensions=['tables', 'fenced_code'])
        
        # Abstract 섹션 체크 (마지막 섹션인 경우)
        if any(x in current_section.lower() for x in ['abstract', '초록']):
            abstract = md_to_inline_html(content_md)
        # 메타 섹션 필터링 (부분 일치 허용)
        elif not any(meta in current_section.lower() for meta in META_SECTIONS):
            if extract_extras:
                essence, keywords = extract_essence_and_keywords(content_html)
                # essence가 비어있으면 content의 첫 500자를 사용
                if not essence:
                    essence = content_html[:500].split('</p>')[0].replace('<p>', '').strip() + "..." if len(content_html) > 500 else content_html.strip()
                sections.append(Section(current_section, content_html,
                                      essence=essence, keywords=keywords))
            else:
                sections.append(Section(current_section, content_html))

    # 명시적 Abstract 섹션이 없으면 수집된 라인 사용
    if not abstract:
        abstract_md = ' '.join(abstract_lines[:5])
        abstract_md = re.sub(r'\s+', ' ', abstract_md).strip()
        if len(abstract_md) > 300:
            abstract_md = abstract_md[:297] + "..."
        abstract = md_to_inline_html(abstract_md)
    
    return sections, subtitle, abstract


def extract_footnotes_from_json(json_path: Path) -> list[Footnote]:
    """JSON 파일에서 각주 추출"""
    footnotes = []
    
    if not json_path.exists():
        print(f"Warning: {json_path} not found. Using empty footnotes.")
        return footnotes
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # bibliography 사용 (있으면)
        if 'bibliography' in data and data['bibliography']:
            for i, citation in enumerate(data['bibliography'], 1):
                footnotes.append(Footnote(i, citation))
        # 또는 footnotes에서 citation_chicago 추출
        elif 'footnotes' in data:
            for i, fn in enumerate(data['footnotes'], 1):
                citation = fn.get('citation_chicago', fn.get('citation', ''))
                if citation:
                    footnotes.append(Footnote(i, citation))
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Error parsing {json_path}: {e}")
    
    return footnotes


def md_to_inline_html(text: str) -> str:
    """Markdown 텍스트를 인라인 HTML로 변환 (p 태그 제거 및 인용구 처리)"""
    # 1. (Source: [ID]) 패턴 처리 -> Styled Span
    # 예: (Source: [ebcf0275]) -> <span class="citation-source text-accent-teal font-bold text-xs" title="Source ID: ebcf0275">[SRC: ebcf0275]</span>
    text = re.sub(r'\(Source: \[?([a-zA-Z0-9]+)\]?\)', 
                  r'<span class="citation-source text-accent-teal font-mono font-bold text-xs cursor-help" title="Source ID: \1">[SRC:\1]</span>', 
                  text)
    
    html = markdown.markdown(text)
    if html.startswith('<p>') and html.endswith('</p>'):
        return html[3:-4]
    return html


def extract_bibliography_from_markdown(md_content: str) -> list[Footnote]:
    """마크다운 참고문헌 섹션에서 항목 추출"""
    footnotes = []
    
    # 코드 블록 전처리
    code_block_pattern = re.compile(r'```(?:markdown|md)?\s*\n(.*?)```', re.DOTALL)
    code_blocks = code_block_pattern.findall(md_content)
    if code_blocks:
        md_content = '\n'.join(code_blocks)
    
    # 참고문헌 섹션 찾기 (여러 패턴 지원)
    bib_patterns = [
        r'###?\s*(?:📚\s*)?(?:선정\s*)?참고문헌.*?\n(.*?)(?=\n##|\n---|\Z)',
        r'###?\s*Selected Bibliography\s*\n(.*?)(?=\n##|\n---|\Z)',
        r'\*\*\[Primary Sources.*?\n(.*?)(?=\n##|\n---|\Z)',
    ]
    
    bib_content = ""
    for pattern in bib_patterns:
        match = re.search(pattern, md_content, re.DOTALL | re.IGNORECASE)
        if match:
            bib_content = match.group(1)
            break
    
    if not bib_content:
        return footnotes
    
    # 각 항목 추출 (* 로 시작하는 항목들)
    items = re.findall(r'^\s*\*\s+(.+?)(?=\n\s*\*|\n\n|\n\*\*\[|\Z)', bib_content, re.MULTILINE | re.DOTALL)
    
    for i, item in enumerate(items, 1):
        citation_md = item.strip().replace('\n', ' ')
        if citation_md and len(citation_md) > 10:
            # Markdown 이탤릭/볼드 등을 HTML로 변환
            citation_html = md_to_inline_html(citation_md)
            footnotes.append(Footnote(i, citation_html))
    
    return footnotes


def extract_footnotes_from_markdown(md_content: str) -> list[Footnote]:
    """마크다운 각주 정의에서 추출"""
    footnotes = []
    
    # [^n]: 패턴 찾기
    pattern = r'\[\^(\d+)\]:\s*(.+?)(?=\n\[\^|\n\n|\Z)'
    matches = re.findall(pattern, md_content, re.DOTALL)
    
    for id_str, citation in matches:
        # Markdown을 HTML로 변환
        citation_html = md_to_inline_html(citation.strip())
        footnotes.append(Footnote(int(id_str), citation_html))
    
    return footnotes


def render_html(topic: str, sections: list[Section], footnotes: list[Footnote], 
                subtitle: str = "", abstract: str = "", 
                mode: str = "full") -> str:
    """Jinja2 템플릿 렌더링"""
    
    # 템플릿 디렉토리 설정
    script_dir = Path(__file__).parent
    template_dir = script_dir / 'templates'
    
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # 모드에 따른 템플릿 선택
    if mode == "condensed":
        template = env.get_template('condensed_template.html')
    else:
        template = env.get_template('base_template.html')
    
    # 타이틀 정리 (첫 번째 단어 또는 토픽명)
    title = topic.replace('_', ' ').replace('-', ' ').title()
    
    # 서브타이틀 기본값
    if not subtitle:
        subtitle = "Theological Research Report"
    
    # Abstract 기본값
    if not abstract:
        abstract = f"A comprehensive research report on {title}, generated by Gemini Scholar Pipeline."
    
    # Full report URL (condensed에서 링크용)
    full_report_url = f"{topic}_report.html"
    
    # 렌더링
    html = template.render(
        title=title,
        subtitle=subtitle,
        abstract=abstract,
        sections=sections,
        footnotes=footnotes,
        quote=None,  # 선택적 인용문 (비활성화)
        full_report_url=full_report_url
    )
    
    return html


def main():
    parser = argparse.ArgumentParser(description='Phase 6: Report Visualization')
    parser.add_argument('--topic', required=True, help='Topic name (e.g., justification)')
    parser.add_argument('--mode', choices=['full', 'condensed', 'both'], 
                        default='both', help='Visualization mode (default: both)')
    parser.add_argument('--suffix', default='', help='File name suffix (e.g., _research)')
    args = parser.parse_args()
    
    topic = args.topic
    mode = args.mode
    suffix = args.suffix
    script_dir = Path(__file__).parent
    reports_dir = script_dir / 'reports'
    
    # 입력 파일 경로
    final_md = reports_dir / f'{topic}_final.md'
    annotated_md = reports_dir / f'{topic}_annotated.md'
    footnotes_json = reports_dir / f'{topic}_footnotes.json'
    
    # _final.md 우선, 없으면 _annotated.md 사용
    if final_md.exists():
        md_path = final_md
    elif annotated_md.exists():
        md_path = annotated_md
    else:
        print(f"Error: No input file found. Expected:")
        print(f"  - {final_md}")
        print(f"  - {annotated_md}")
        return
    
    print(f"[Phase 6] Report Visualization")
    print(f"  Input: {md_path.name}")
    print(f"  Mode: {mode}")
    
    # 마크다운 읽기
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 각주 추출 (JSON 우선, 없으면 마크다운에서)
    footnotes = extract_footnotes_from_json(footnotes_json)
    if not footnotes:
        # 마크다운 각주 정의에서 추출
        footnotes = extract_footnotes_from_markdown(md_content)
    if not footnotes:
        # 참고문헌 섹션에서 추출
        footnotes = extract_bibliography_from_markdown(md_content)
    print(f"  Footnotes found: {len(footnotes)}")
    
    # Full 모드 생성
    if mode in ['full', 'both']:
        sections, subtitle, abstract = parse_markdown_sections(md_content, extract_extras=False)
        print(f"  [Full] Sections parsed: {len(sections)}")
        
        html = render_html(topic, sections, footnotes, subtitle, abstract, mode="full")
        output_path = reports_dir / f'{topic}{suffix}_report.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  [Full] Output: {output_path.name}")
    
    # Condensed 모드 생성
    if mode in ['condensed', 'both']:
        sections, subtitle, abstract = parse_markdown_sections(md_content, extract_extras=True)
        print(f"  [Condensed] Sections parsed: {len(sections)}")
        
        html = render_html(topic, sections, footnotes, subtitle, abstract, mode="condensed")
        output_path = reports_dir / f'{topic}{suffix}_brief.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  [Condensed] Output: {output_path.name}")
    
    print(f"[Phase 6] Complete!")


if __name__ == '__main__':
    main()
