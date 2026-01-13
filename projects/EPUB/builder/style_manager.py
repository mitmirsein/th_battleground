
import os

class StyleManager:
    """
    EPUB용 CSS 스타일을 생성 및 관리 (Theology Edition)
    """
    
    def generate_css(self, theme: str = 'default') -> str:
        """테마에 맞는 CSS 문자열 반환"""
        
        # 공통 리셋 및 기본 설정
        common_css = """
/* Reset & Base */
@namespace epub "http://www.idpf.org/2007/ops";
body {
    margin: 0;
    padding: 0;
    text-align: justify;
    -webkit-text-size-adjust: 100%;
}

/* Links */
a {
    text-decoration: none;
    color: inherit;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.5em auto;
    break-inside: avoid;
}
figure {
    margin: 1.5em 0;
    text-align: center;
}
figcaption {
    font-size: 0.9em;
    font-style: italic;
    color: #666;
    margin-top: 0.5em;
}

/* Footnotes */
aside[epub|type~="footnote"],
div.footnotes {
    border-top: 1px solid #ccc;
    margin-top: 2em;
    padding-top: 1em;
    font-size: 0.85em;
    color: #444;
}

/* Code */
code {
    background-color: #f5f5f5;
    padding: 0.1em 0.3em;
    border-radius: 2px;
    font-family: monospace;
    font-size: 0.9em;
}
"""

        # 테마별 설정
        if theme == 'shinhak_paper':  # 종이책 느낌 (세리프)
            return common_css + self._get_shinhak_paper_css()
        elif theme == 'shinhak_screen': # 스크린 최적화 (산세리프)
            return common_css + self._get_shinhak_screen_css()
        else:
            return common_css + self._get_default_css()

    def _get_shinhak_paper_css(self) -> str:
        """신학 서적 (종이책 스타일) - 권위있고 차분함"""
        return """
/* Typography: Serif (KoPubBatang equiv) */
body {
    font-family: "KoPubBatang Medium", "Noto Serif KR", serif;
    font-size: 1.0em;
    line-height: 1.7;
    color: #111;
    padding: 0 3%;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    font-family: "KoPubDotum Bold", "Noto Sans KR", sans-serif;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 2em;
    margin-bottom: 0.8em;
    line-height: 1.3;
}

h1 {
    font-size: 2.2em;
    text-align: center;
    border-bottom: 2px solid #8B0000; /* Dark Red accent */
    padding-bottom: 0.5em;
    margin-bottom: 1.5em;
}

h2 {
    font-size: 1.6em;
    border-left: 5px solid #8B0000;
    padding-left: 0.5em;
}

h3 {
    font-size: 1.3em;
    color: #444;
}

/* Paragraphs */
p {
    margin-bottom: 0;
    text-indent: 1.2em;
    margin-top: 0.5em;
}
p.no-indent {
    text-indent: 0;
}

/* Blockquotes (Theological quotes) */
blockquote {
    font-family: "KoPubDotum Light", sans-serif;
    margin: 1.5em 2em;
    padding: 0.5em 1em;
    border-left: 3px solid #8B0000;
    background-color: #f9f9f9;
    font-size: 0.95em;
    color: #333;
}

/* Glossary Terms (Strong) */
strong {
    color: #2c3e50; /* Dark Blue-Grey for Terms */
    font-weight: bold;
}

/* Bible References */
.bible-ref {
    font-variant: small-caps;
    color: #000000; /* Black as requested */
    font-weight: normal; /* Regular weight for contrast with terms */
}

/* Small Text (Parentheses) */
.small-text {
    font-size: 0.85em;
    vertical-align: baseline;
}

/* Map Links (Google Maps) */
a.map-link {
    color: #2e8b57; /* SeaGreen - distinct from normal blue links */
    text-decoration: underline;
}

/* List Items (Glossary Definitions) - Hanging Indent & Spacing */
/* List Items (Glossary Definitions) - Custom Bullet with Unified Spacing */
ul {
    list-style-type: none;
    padding-left: 1.5em;
    margin-top: 0.5em;
}

li {
    position: relative;
    margin-bottom: 0.6em;
    text-align: justify;
    line-height: 1.6;
}

li::before {
    content: "•";
    position: absolute;
    left: -1.2em; /* Precise control of bullet position */
    top: 0;
    width: 1em;
    text-align: center;
    color: #000000;
}


/* Title Page */
.title-page {
    text-align: center;
    margin-top: 20%;
    page-break-after: always;
}
.title-page h1 {
    font-size: 2.5em;
    margin-bottom: 0.5em;
    color: #2c3e50;
}
.title-page .author {
    font-size: 1.2em;
    color: #555;
    margin-top: 2em;
}
.title-page hr {
    width: 50%;
}

/* Intro Page */
.intro-page {
    margin-top: 20%;
    text-align: center;
    page-break-after: always;
}
.intro-page h2 {
    color: #2c3e50;
    margin-bottom: 1em;
}
.intro-page ul {
    list-style-type: none;
    padding-left: 0;
}
.intro-page li {
    margin-bottom: 0.8em;
    text-align: center;
    text-indent: 0;
}
.intro-page li::before {
    content: none;
}

/* Centered Section (Bibliography) */
.centered-section {
    text-align: center;
}
.centered-section h1, .centered-section h2 {
    text-align: center;
}
.centered-section ul {
    list-style-type: none;
    padding-left: 0;
}
.centered-section li {
    margin-bottom: 0.5em;
    text-align: center;
    text-indent: 0;
}
.centered-section li::before {
    content: none;
}    margin: 3em auto;
    border: 0;
    border-top: 1px solid #ccc;
}
"""

    def _get_shinhak_screen_css(self) -> str:
        """신학 서적 (스크린용) - 가독성 중심"""
        return """
/* Typography: Sans-Serif (Pretendard/Noto Sans equiv) */
body {
    font-family: "Pretendard", "Noto Sans KR", sans-serif;
    font-size: 1.1em;
    line-height: 1.5;
    color: #222;
}

/* Headers */
h1, h2, h3 {
    color: #003366; /* Navy Blue */
    font-weight: 700;
    margin-top: 1.5em;
}

h1 { font-size: 1.8em; text-align: left; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }
h2 { font-size: 1.4em; }
h3 { font-size: 1.2em; }

/* Paragraphs */
p {
    margin-bottom: 1em;
    text-indent: 0; /* 스크린에선 들여쓰기 대신 여백 */
    display: block;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #003366;
    background-color: #f0f4f8;
    margin: 1em 0;
    padding: 1em;
    border-radius: 4px;
}

/* Bible References */
.bible-ref {
    color: #003366;
    background_color: #e6f0ff;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}
"""

    def _get_default_css(self) -> str:
        return """
body { font-family: sans-serif; line-height: 1.6; }
h1, h2, h3 { color: #333; }
blockquote { border-left: 4px solid #ccc; margin: 1em; padding-left: 1em; }
"""

    def save_css(self, css_content: str, output_path: str):
        """CSS 파일로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
