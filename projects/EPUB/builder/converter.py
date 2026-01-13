import re
import os

class HtmlTxtConverter:
    """
    Converts specific HTML-like text files (e.g., Glossary output) to clean Markdown.
    Preprocessing rules:
    1. Header Conversion: <h1> -> #, <p class="p17"> -> ##
    2. Format Definitions: <p class="p18"> -> - **Term**: Definition
       - Detects terms via <span class="c2"> OR first colon separator
    3. Cleanup: 
       - Remove HTML tags
       - Decode entities
       - Normalize whitespace (single line per entry)
       - Strip leading/trailing whitespace
       - Standardize sentence endings (Polite -> Plain, Noun -> ~이다)
    """

    def __init__(self):
        pass

    def convert(self, input_path: str, output_path: str = None) -> str:
        """
        Reads input file, applies conversion rules, and writes to output_path.
        If output_path is not provided, it defaults to changing extension to .md.
        Returns the path to the converted file.
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Main Header
        # <h1 class="p10" ...>용어 해설</h1> -> # 용어 해설
        content = re.sub(r'<h1.*?>\s*(?:<span.*?>)?(.*?)(?:</span>)?\s*</h1>', r'# \1\n', content)

        # 2. Section Headers
        # <p class="p17" ...>A. 욥의 원래 이야기</p> -> ## A. 욥의 원래 이야기
        content = re.sub(r'<p class="p17".*?>\s*(.*?)\s*</p>', r'\n## \1\n', content)

        # 3. Terms and Definitions
        # <p class="p18" ...><span class="c2">Term</span><span class="c2 c3">: Definition...</span></p>
        
        def parse_term(match):
            p_content = match.group(1)
            
            # Extract Term via Span class "c2"
            term_match = re.search(r'<span class="c2">(.*?)</span>', p_content)
            
            # Formatting logic
            if not term_match:
                # Clean HTML tags and normalize whitespace first
                cleaned = re.sub(r'<[^>]+>', '', p_content).strip()
                cleaned = re.sub(r'\s+', ' ', cleaned)
                
                # Check for colon pattern (Term: Definition)
                # Use maxsplit=1 to only split on the first colon
                if ':' in cleaned:
                    parts = cleaned.split(':', 1)
                    term_text = parts[0].strip()
                    def_text = parts[1].strip()
                    return f'- **{term_text}**: {def_text}'
                
                # Fallback: Check if empty
                if not cleaned: 
                    return ''
                # Format as a list item
                return f'- {cleaned}'
                
            term = term_match.group(1).strip()
            
            # Extract Definition (everything after the term span)
            def_content = p_content[term_match.end():]
            
            # Clean HTML tags from definition
            def_clean = re.sub(r'<[^>]+>', '', def_content).strip()
            
            # Normalize whitespace: replace newlines and multiple spaces with a single space
            def_clean = re.sub(r'\s+', ' ', def_clean)
            
            # Convert polite endings (입니다, 습니다) to plain form
            def_clean = self._convert_polite_to_plain(def_clean)
            
            # Remove leading colons if present (often ": Definition")
            if def_clean.startswith(':'):
                def_clean = def_clean[1:].strip()
                
            # Filter empty definitions if term is empty (unlikely with regex) or definition is empty
            if not term and not def_clean:
                return ''

            # Format: **Term**: Definition
            return f'- **{term}**: {self._normalize_ending(def_clean)}'

        content = re.sub(r'<p class="p18".*?>(.*?)</p>', parse_term, content, flags=re.DOTALL)

        # 4. General HTML & Entity Cleanup
        # Remove remaining specific classes (empty lines like p3)
        content = re.sub(r'<p class="p3".*?>.*?</p>', '', content) 
        
        # Decode entities
        content = re.sub(r'&quot;', '"', content)
        content = re.sub(r'&lt;', '<', content)
        content = re.sub(r'&gt;', '>', content)
        
        # Remove any other remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # 5. Structure Cleanup
        # Remove multiple newlines and empty list items
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Strip leading/trailing whitespace from each line and filter empty lines
        lines = []
        for line in content.split('\n'):
            stripped = line.strip()
            # Filter out lines that are just a hyphen (empty list item)
            if stripped == '-': 
                continue
            lines.append(stripped)
        content = '\n'.join(lines)
        
        if not content.startswith('---'):
            frontmatter = """---
title: '용어 해설'
author: 'MSN'
language: 'ko'
---

<div class="title-page">

# 용어 해설

<h3 style="color: grey;">[테스트 샘플]</h3>

<div class="author">MSN</div>

<hr/>

</div>

<div class="intro-page">

## 일러두기

- [초록색 밑줄]{style="color: #2e8b57; text-decoration: underline;"}이 있는 지명은 **구글 지도**로 연결됩니다.
- 성경 장절(예: [창 1:1]{.bible-ref})을 클릭하면 **YouVersion 성경(새번역)** 웹사이트로 연결됩니다.
- 본문 중 **다른 용어 항목**이 언급될 경우 자동으로 링크가 연결됩니다.

<hr/>

</div>
"""
            content = frontmatter + content

        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = base + ".md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return output_path

    def _convert_polite_to_plain(self, text: str) -> str:
        """
        높임말(경어체)을 평어체로 변환
        - 입니다 -> 이다
        - 습니다 -> 다 (었/았/였/했/쳤/있/없/겠 등)
        """
        # 입니다 -> 이다
        text = re.sub(r'입니다', '이다', text)
        
        # (과거/존재/미래) 습니다 -> 다
        text = re.sub(r'(있|없|었|았|였|했|쳤|겠)습니다', r'\1다', text)
        
        # Add more mappings if found
        
        return text

    def _normalize_ending(self, text: str) -> str:
        """
        문장 어미 통일 (~이다).
        - '다'로 끝나면 (괄호/따옴표 포함) 그대로 유지
        - '참조'로 끝나면 그대로 유지
        - 그 외는 '이다'를 붙임
        """
        if not text:
            return ""
            
        # Remove existing trailing period/whitespace
        stem = text.rstrip(" .")
        
        if not stem:
            return ""

        # Check ending:
        # 1. '다' or '참조' (Verbs/Adjectives/Refs) - Matches literal '다' char
        # 2. Optional closing punctuation
        # 3. Optional parenthetical citation
        if re.search(r'(다|참조)[\)\]"\'”’]*(\s*[\(\[].*?[\)\]])?$', stem):
            return stem + "."
        else:
            # 명사형 등으로 끝나는 경우 '이다.' 추가
            return stem + "이다."
