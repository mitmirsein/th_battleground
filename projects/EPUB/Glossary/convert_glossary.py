
import re
import os

def convert_glossary(input_path, output_path):
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
    # Logic:
    # - Find p18 paragraphs
    # - Extract first span (c2) as Term
    # - Extract rest as definition (removing tags)
    
    def parse_term(match):
        p_content = match.group(1)
        
        # Extract Term
        term_match = re.search(r'<span class="c2">(.*?)</span>', p_content)
        
        # Scenario 1: No span class="c2" found
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
            
            # Fallback: Format as a list item even without a specific bold term
            return f'- {cleaned}'
            
        term = term_match.group(1).strip()
        
        # Extract Definition (everything after the term span)
        # Remove the term span from content
        def_content = p_content[term_match.end():]
        
        # Clean HTML tags from definition
        def_clean = re.sub(r'<[^>]+>', '', def_content).strip()
        
        # Normalize whitespace: replace newlines and multiple spaces with a single space
        def_clean = re.sub(r'\s+', ' ', def_clean)
        
        # Remove leading colons if present (often ": Definition")
        if def_clean.startswith(':'):
            def_clean = def_clean[1:].strip()
            
        # Format: **Term**: Definition
        return f'- **{term}**: {def_clean}'

    content = re.sub(r'<p class="p18".*?>(.*?)</p>', parse_term, content, flags=re.DOTALL)

    # 4. Cleanup
    # Remove remaining HTML tags (like empty <p>)
    content = re.sub(r'<p class="p3".*?>.*?</p>', '', content) # Empty lines
    content = re.sub(r'&quot;', '"', content)
    content = re.sub(r'&lt;', '<', content)
    content = re.sub(r'&gt;', '>', content)
    # Remove other HTML tags left
    content = re.sub(r'<[^>]+>', '', content)
    
    # Remove multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Final cleanup: Remove leading/trailing whitespace from each line to prevent code block formatting
    lines = [line.strip() for line in content.split('\n')]
    content = '\n'.join(lines)

    # Add Frontmatter
    frontmatter = """---
title: '용어 해설'
author: 'MSN'
language: 'ko'
---

"""
    result = frontmatter + content

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
        
    print(f"✅ Converted {input_path} -> {output_path}")

if __name__ == "__main__":
    convert_glossary("Glossary.txt", "Glossary.md")
