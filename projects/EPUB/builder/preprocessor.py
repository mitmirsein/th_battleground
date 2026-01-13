
import re
import os
from typing import Tuple, List, Dict

class MarkdownPreprocessor:
    """
    Obsidian 마크다운을 Pandoc 호환 표준 마크다운으로 변환하는 전처리기
    Ported from MarkdownPreprocessor.ts
    """

    def __init__(self, base_path: str = '.'):
        self.base_path = os.path.abspath(base_path)

    def preprocess(self, content: str, source_path: str) -> str:
        """메인 전처리 파이프라인"""
        
        # 참고문헌 수집 초기화
        self.bib_matched = {'dicts': set(), 'books': set()}
        
        # 1. 미디어 임베드 제거 (오디오/비디오) - 단순화
        # ![[...mp3]], ![[...mp4]] 등은 제외
        
        # 2. Obsidian 이미지 문법 변환 (![[image.png]])
        content = self._convert_obsidian_images(content)
        
        # 3. Obsidian 위키링크 변환 ([[Link]])
        content = self._convert_obsidian_links(content)
        
        # 4. 하이라이트 변환 (==text== -> **text**)
        content = self._convert_highlights(content)
        
        # 5. 성경 레퍼런스 포맷팅 (Feature 3)
        # (Gen 1:1) 또는 [Gen 1:1] 형태를 <span class="bible-ref">로 감싸기
        content = self._format_bible_refs(content)
        
        # 6. 책 제목 이탤릭체 적용 (영문/독문)
        content = self._format_book_titles(content)
        
        # 7. 괄호 텍스트 작게 처리
        content = self._format_parentheses(content)
        
        # 8. 상호 참조 링크 생성 (Backlinks)
        content = self._link_cross_references(content)
        
        # 9. 구글 지도 링크 (NEW)
        content = self._link_locations(content)
        
        # 10. 참고문헌 섹션 추가
        content = self._append_bibliography(content)
        
        return content

    def _convert_obsidian_images(self, content: str) -> str:
        """
        ![[Image.png]] -> ![Image.png](Image.png)
        ![[Image.png|Caption]] -> ![Caption](Image.png)
        """
        # 패턴: ![[파일명|캡션]] 또는 ![[파일명]]
        pattern = r'!\[\[(.*?)(?:\|(.*?))?\]\]'
        
        def replace_func(match):
            filename = match.group(1).strip()
            caption = match.group(2).strip() if match.group(2) else filename
            
            # TODO: 여기서 이미지 절대 경로를 찾아야 함 (현재는 상대 경로 가정)
            return f'![{caption}]({filename})'
            
        return re.sub(pattern, replace_func, content)

    def _convert_obsidian_links(self, content: str) -> str:
        """
        [[Link]] -> [Link](Link)
        [[Link|Text]] -> [Text](Link)
        """
        pattern = r'(?<!\!)\[\[(.*?)(?:\|(.*?))?\]\]'
        
        def replace_func(match):
            link = match.group(1).strip()
            text = match.group(2).strip() if match.group(2) else link
            
            return f'[{text}]({link})'
            
        return re.sub(pattern, replace_func, content)

    def _convert_highlights(self, content: str) -> str:
        """
        ==Text== -> **Text**
        """
        pattern = r'==(.*?)=='
        return re.sub(pattern, r'**\1**', content)
        
    def _format_bible_refs(self, content: str) -> str:
        """
        성경 구절 패턴을 찾아 외부 링크(Bible.com)로 변환
        - 컨텍스트 유지: 같은 라인 내에서 책 이름이 언급되면 이후 생략된 참조도 해당 책으로 연결
        - 예: 욥 42:11 ... (42:10) -> 둘 다 Job으로 연결
        """
        bible_map = {
            '창': 'GEN', '출': 'EXO', '레': 'LEV', '민': 'NUM', '신': 'DEU',
            '수': 'JOS', '삿': 'JDG', '룻': 'RUT', '삼상': '1SA', '삼하': '2SA',
            '왕상': '1KI', '왕하': '2KI', '대상': '1CH', '대하': '2CH', '스': 'EZR',
            '느': 'NEH', '에': 'EST', '욥': 'JOB', '시': 'PSA', '잠': 'PRO',
            '전': 'ECC', '아': 'SNG', '사': 'ISA', '렘': 'JER', '애': 'LAM',
            '겔': 'EZK', '단': 'DAN', '호': 'HOS', '욜': 'JOL', '암': 'AMO',
            '옵': 'OBA', '욘': 'JON', '미': 'MIC', '나': 'NAM', '합': 'HAB',
            '습': 'ZEP', '학': 'HAG', '슥': 'ZEC', '말': 'MAL',
            '마': 'MAT', '막': 'MRK', '눅': 'LUK', '요': 'JHN', '행': 'ACT',
            '롬': 'ROM', '고전': '1CO', '고후': '2CO', '갈': 'GAL', '엡': 'EPH',
            '빌': 'PHP', '골': 'COL', '살전': '1TH', '살후': '2TH', '딤전': '1TI',
            '딤후': '2TI', '딛': 'TIT', '몬': 'PHM', '히': 'HEB', '약': 'JAS',
            '벧전': '1PE', '벧후': '2PE', '요1': '1JN', '요2': '2JN', '요3': '3JN',
            '유': 'JUD', '계': 'REV'
        }
        
        # Regex: (Optional Book)(Verse)
        regex_compiled = re.compile(r'(?:([1-3]?[A-Za-z가-힣]+)\s+)?(\d+[:.]\d+(?:[-~,]\d+)*)')

        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Per-line context reset
            current_book_code = None
            
            def replace_with_context(match):
                nonlocal current_book_code
                
                book_str = match.group(1) # None if implicit
                ref_str = match.group(2)
                full_match = match.group(0)
                
                # Check 1: Is there an explicit book?
                if book_str:
                    code = bible_map.get(book_str.strip())
                    if code:
                        current_book_code = code
                        clean_ref = ref_str.replace(':', '.')
                        url = f"https://www.bible.com/ko/bible/142/{code}.{clean_ref}.RNKSV"
                        return f'<a href="{url}" class="bible-ref" target="_blank">{full_match}</a>'
                    else:
                        # Explicit book but not in bible map (e.g. dictionary)
                        return f'<span class="bible-ref">{full_match}</span>'
                
                # Check 2: Implicit (No book), but have context?
                elif current_book_code:
                    clean_ref = ref_str.replace(':', '.')
                    url = f"https://www.bible.com/ko/bible/142/{current_book_code}.{clean_ref}.RNKSV"
                    return f'<a href="{url}" class="bible-ref" target="_blank">{full_match}</a>'
                
                # Check 3: Implicit, No context -> No change
                else:
                    return full_match
            
            new_line = regex_compiled.sub(replace_with_context, line)
            new_lines.append(new_line)
            
        return '\n'.join(new_lines)

    def _format_book_titles(self, content: str) -> str:
        """
        영문/독문 책 제목 이탤릭체 적용 + 참고문헌 수집
        1. 신학 사전 약어 (ThWAT 등)
        2. 인용구 내의 서명 패턴 (Author, Title, Page)
        """
        # 1. Known Standard Abbreviations
        abbrs = [
            "ThWAT", "TWAT", "DNP", "BHHWB", "TDNT", "THAT", 
            "EKL", "TRE", "RGG", "AB", "ABD", "IDB"
        ]
        # Word boundary to avoid partial matches
        abbr_pattern = r'\b(' + '|'.join(abbrs) + r')\b'
        
        def replace_abbr(match):
            term = match.group(1)
            self.bib_matched['dicts'].add(term)
            return f'*{term}*'
            
        content = re.sub(abbr_pattern, replace_abbr, content)

        # 2. Citation Pattern: (Author, Title, Page)
        # Regex: (comma or paren) (Title) (comma and digit)
        # Excluding patterns that might just be "City, Year"
        regex = r'([\(\,]\s*)([A-ZÄÖÜ][a-zA-Z0-9äöüÄÖÜß\s\.\-&]+?)(,\s*\d+)'
        
        # Exclude list (Publishers, etc.)
        exclude_titles = ["Verlag Junge Gemeinde", "Stuttgart"]
        
        def replace_book(match):
            prefix = match.group(1)
            title = match.group(2).strip()
            suffix = match.group(3)
            
            if title in exclude_titles:
                return match.group(0)
                
            # Heuristic: Check formatting/length
            if len(title) < 2:
                return match.group(0)
                
            self.bib_matched['books'].add(title)
            return f'{prefix}*{title}*{suffix}'
            
        content = re.sub(regex, replace_book, content)
        
        return content

    def _format_parentheses(self, content: str) -> str:
        """
        괄호와 괄호 속 문자를 본문보다 작게 처리
        Markdown 링크의 URL 부분은 제외: ](...) 형태는 건너뜀
        """
        # Negative lookbehind (?<!\]) ensures we don't match the url part of [text](url)
        # Matches (text) pattern
        regex = r'(?<!\])(\([^\)]+\))'
        
        def replace_paren(match):
            text = match.group(1)
            return f'<span class="small-text">{text}</span>'
            
        return re.sub(regex, replace_paren, content)

    def _link_cross_references(self, content: str) -> str:
        """
        글로서리 항목 간 상호 참조 링크 생성 (Backlinks)
        1. 모든 항목어(Term) 추출 및 Anchor ID 생성
        2. 본문에서 다른 항목어가 등장하면 링크로 변환
        3. 의미 매칭을 위해 부연설명(괄호) 제거 후 핵심어(Core Term)만 매칭
        """
        lines = content.split('\n')
        
        # 1. 항목어 추출 & ID 매핑
        # 패턴: "- **Term**:"
        term_map = {} # {core_term: term_id}
        regex_term = re.compile(r'^-\s*\*\*(.*?)\*\*:')
        
        for line in lines:
            match = regex_term.match(line)
            if match:
                raw_term = match.group(1)
                
                # HTML 태그 제거
                clean_term = re.sub(r'<[^>]+>', '', raw_term)
                # 괄호 및 내용 제거 (핵심어 추출)
                core_term = re.sub(r'\s*\(.*?\)', '', clean_term).strip()
                
                # 유효성 검사: 너무 짧은 단어 제외
                if len(core_term) < 2:
                    continue
                
                # ID 생성
                safe_id = f"term-{abs(hash(core_term))}"
                term_map[core_term] = safe_id
        
        # 긴 단어부터 처리
        sorted_terms = sorted(term_map.keys(), key=len, reverse=True)
        
        # 2. 앵커 주입 및 링크 변환
        new_lines = []
        
        for line in lines:
            match = regex_term.match(line)
            if match:
                # 정의 라인
                raw_term = match.group(1)
                clean_term = re.sub(r'<[^>]+>', '', raw_term)
                current_core = re.sub(r'\s*\(.*?\)', '', clean_term).strip()
                
                term_id = term_map.get(current_core)
                
                if term_id:
                    # Anchor 주입
                    prefix = f"- <span id='{term_id}'></span>**{raw_term}**:"
                    rest = line[match.end():]
                    
                    # exclude_term은 current_core
                    linked_rest = self._apply_links(rest, sorted_terms, term_map, exclude_term=current_core)
                    new_lines.append(prefix + linked_rest)
                else:
                    prefix = f"- **{raw_term}**:"
                    rest = line[match.end():]
                    linked_rest = self._apply_links(rest, sorted_terms, term_map)
                    new_lines.append(prefix + linked_rest)
            else:
                linked_line = self._apply_links(line, sorted_terms, term_map)
                new_lines.append(linked_line)
                
        return '\n'.join(new_lines)

    def _apply_links(self, text: str, sorted_terms: list, term_map: dict, exclude_term: str = None) -> str:
        """
        Text 내에서 terms를 찾아 링크로 변환.
        기존 링크나 HTML 태그 내부를 보호함.
        """
        placeholders = {}
        
        def save_match(match):
            key = f"__PH_{len(placeholders)}__"
            placeholders[key] = match.group(0)
            return key

        # 보호할 패턴들
        regex_md_link = r'!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)'
        regex_html_tag_only = r'<[^>]+>' 
        
        text = re.sub(regex_md_link, save_match, text)
        text = re.sub(regex_html_tag_only, save_match, text)
        
        for term in sorted_terms:
            if term == exclude_term:
                continue
            
            # 왼쪽 경계 체크: 다리우스(Darius) 안에 우스(Uz)가 매칭되는 것 방지
            # (?<![가-힣a-zA-Z0-9]) : 앞에 한글/영문/숫자가 없어야 함
            boundary_pattern = r'(?<![가-힣a-zA-Z0-9])'
            pattern = boundary_pattern + re.escape(term)
            
            if re.search(pattern, text):
                term_id = term_map[term]
                
                def replace_term(m):
                    link = f"[{term}](#{term_id})"
                    k = f"__PH_{len(placeholders)}__"
                    placeholders[k] = link
                    return k

                text = re.sub(pattern, replace_term, text)

        # 복구 (Placeholders)
        # 생성된 순서 상관없이 모든 키를 찾아 치환
        # 중첩된 PH가 없다고 가정 (위 로직상 PH 안에 PH는 replace_term에서만 발생)
        # 하지만 replace_term의 PH값은 MD Link 형식이므로, 
        # 초기 protection에서 잡히는 MD link와 구문상 같지만, 이미 PH로 치환됨.
        
        # 반복 치환 (순서 의존성 해결)
        for _ in range(3): 
            found = False
            for k, v in placeholders.items():
                if k in text:
                    text = text.replace(k, v)
                    found = True
            if not found:
                break
                
        return text

    def _link_locations(self, content: str) -> str:
        """
        지명 텍스트를 감지하여 구글 지도 링크로 변환
        - 배제: 이미 링크된 텍스트, HTML 태그 내부
        """
        locations = {
            '예루살렘': 'Jerusalem', '헤브론': 'Hebron', '니푸르': 'Nippur', 
            '우가릿': 'Ugarit', '테베': 'Thebes, Egypt', '멤피스': 'Memphis, Egypt', 
            '수사': 'Susa', '바빌론': 'Ancient Babylon', '나일강': 'Nile', 
            '유프라테스': 'Euphrates', '티그리스': 'Tigris', '아테네': 'Athens', 
            '룩소르': 'Luxor', '카르낙': 'Karnak', '갈릴리': 'Galilee', 
            '사마리아': 'Samaria', '요단강': 'Jordan River', '시내산': 'Mount Sinai', 
            '에돔': 'Edom', '모압': 'Moab', '암몬': 'Ammon', '아람': 'Aram', 
            '아시리아': 'Assyria', '페르시아': 'Persia', '이집트': 'Egypt',
            '비수툰': 'Behistun', '에스-사파': 'Es-Safa', '다마스쿠스': 'Damascus',
            '수에즈 운하': 'Suez Canal', '수에즈 만': 'Gulf of Suez',
            '시르보니스 호수': 'Lake Bardawil', '지중해': 'Mediterranean Sea',
            '나일강 삼각주': 'Nile Delta',
            '마라톤': 'Marathon, Greece', '아라비아': 'Arabia'
        }
        
        sorted_locs = sorted(locations.keys(), key=len, reverse=True)
        
        placeholders = {}
        def save_match(match):
            key = f"__PH_LOC_{len(placeholders)}__"
            placeholders[key] = match.group(0)
            return key

        # Protect existing links/tags/anchors
        regex_link = r'!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|<a\s+[^>]*>.*?</a>'
        regex_tag = r'<[^>]+>'
        
        content = re.sub(regex_link, save_match, content)
        content = re.sub(regex_tag, save_match, content)
        
        for loc in sorted_locs:
            query = locations[loc]
            # Left Boundary only (allow particles on right)
            pattern = r'(?<![가-힣a-zA-Z0-9])' + re.escape(loc)
            
            # Check if the location exists in the content before attempting to replace
            # This prevents unnecessary regex operations and placeholder creation
            if re.search(pattern, content):
                def replace_loc(m):
                    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                    link = f'<a href="{url}" class="map-link" target="_blank">{loc}</a>'
                    k = f"__PH_LOC_{len(placeholders)}__"
                    placeholders[k] = link
                    return k
                content = re.sub(pattern, replace_loc, content)

        # Restore
        for _ in range(3):
            found = False
            for k, v in placeholders.items():
                if k in content:
                    content = content.replace(k, v)
                    found = True
            if not found:
                break
                
        return content

    def _append_bibliography(self, content: str) -> str:
        """
        수집된 참고문헌(사전, 단행본) 목록을 문서 끝에 추가
        기존에 '참고문헌' 헤더가 있다면 제거 후 재생성
        """
        if not self.bib_matched['dicts'] and not self.bib_matched['books']:
            return content
        
        # Remove existing header if it exists at the end
        # Remove existing header if it exists at the end
        content = re.sub(r'#\s*참고문헌\s*$', '', content.strip())
            
        bib_section = '\n\n<div class="centered-section">\n\n'
        bib_section += "# 참고문헌\n\n"
        
        # 사전류
        if self.bib_matched['dicts']:
            bib_section += "## 사전류\n\n"
            for d in sorted(self.bib_matched['dicts']):
                bib_section += f"- {d}\n"
            bib_section += "\n"
            
        # 단행본류
        if self.bib_matched['books']:
            bib_section += "## 단행본류\n\n"
            # 알파벳 순 정렬
            for b in sorted(self.bib_matched['books']):
                bib_section += f"- *{b}*\n"
        
        bib_section += "\n</div>"
                
        return content + bib_section

