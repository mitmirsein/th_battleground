
import os
import argparse
import sys
from .core import EpubBuilder
from .preprocessor import MarkdownPreprocessor
from .style_manager import StyleManager
from .converter import HtmlTxtConverter

def main():
    parser = argparse.ArgumentParser(description="Theology EPUB Builder")
    parser.add_argument("input", help="입력 마크다운 파일 경로")
    parser.add_argument("-o", "--output", help="출력 EPUB 파일 경로 (기본: input.epub)")
    parser.add_argument("--title", help="책 제목 (기본: 파일명)")
    parser.add_argument("--author", help="저자")
    parser.add_argument("--theme", default="default", help="CSS 테마 (default, shinhak)")
    parser.add_argument("--keep-temp", action="store_true", help="중간 단계 임시 파일 보존")
    
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: 파일이 존재하지 않습니다: {input_path}")
        sys.exit(1)

    # 0. 텍스트 파일(HTML-like glossary) 자동 변환
    if input_path.lower().endswith('.txt'):
        print(f"🔄 Detected raw text input: {input_path}")
        print("   Running HtmlTxtConverter...")
        converter = HtmlTxtConverter()
        # 변환된 파일 경로로 input_path 교체 (예: Glossary.txt -> Glossary.md)
        input_path = converter.convert(input_path) 
        print(f"   Converted to source: {input_path}")
        
    # 출력 경로 설정
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{base_name}.epub")
        
    # 제목 설정
    title = args.title if args.title else os.path.splitext(os.path.basename(input_path))[0]
    
    print(f"📘 Building EPUB: {title}")
    
    # 1. CSS 생성
    print("🎨 Generating styles...")
    style_mgr = StyleManager()
    css_content = style_mgr.generate_css(args.theme)
    temp_css_path = "temp_style.css"
    style_mgr.save_css(css_content, temp_css_path)
    
    # 2. 마크다운 전처리
    print("📝 Preprocessing markdown...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        preprocessor = MarkdownPreprocessor()
        processed_content = preprocessor.preprocess(content, input_path)
        
        temp_md_path = "temp_manuscript.md"
        with open(temp_md_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
            
    except Exception as e:
        print(f"Error reading/processing file: {e}")
        sys.exit(1)
        
    # 3. EPUB 빌드
    print("🚀 Running Pandoc...")
    builder = EpubBuilder()
    
    if not builder.check_availability():
        print("Error: Pandoc이 설치되어 있지 않습니다. (brew install pandoc)")
        sys.exit(1)
        
    # 표지 이미지 자동 감지
    input_dir = os.path.dirname(input_path)
    cover_path = os.path.join(input_dir, "cover.png")
    if not os.path.exists(cover_path):
        cover_path = None
    else:
        print(f"🖼️  Detected cover image: {cover_path}")

    success = builder.build(
        input_path=temp_md_path, # 전처리된 파일 사용
        output_path=output_path,
        title=title,
        author=args.author,
        css_path=temp_css_path,
        cover_image=cover_path,
        # TODO: 폰트 파일이 실제 존재하는지 확인 후 추가해야 함
        fonts=[] 
    )
    
    # 4. 정리
    if not args.keep_temp:
        if os.path.exists(temp_css_path): os.remove(temp_css_path)
        if os.path.exists(temp_md_path): os.remove(temp_md_path)
        print("🧹 Cleaned up temporary files.")
        
    if success:
        print(f"✅ Created: {output_path}")
    else:
        print("❌ Build failed.")

if __name__ == "__main__":
    main()
