#!/usr/bin/env python3
"""
Lecture Video Generator - Main Pipeline

Usage:
    python pipeline.py generate input/lecture.md    # 개요 + 슬라이드 생성
    python pipeline.py tts input/lecture.md         # TTS 생성 (Phase 2)
    python pipeline.py assemble input/              # 영상 조립 (Phase 3)
    python pipeline.py all input/lecture.md         # 전체 파이프라인
"""
import argparse
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import INPUT_DIR, OUTPUT_DIR, GOOGLE_API_KEY
from modules.lecture_parser import LectureParser
from modules.outline_generator import OutlineGenerator
from modules.slide_generator import SlideGenerator


def cmd_generate(args):
    """개요 + 슬라이드 생성"""
    input_file = Path(args.input)
    output_dir = Path(args.output) if args.output else OUTPUT_DIR / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Lecture Video Generator: generate")
    print(f"   입력: {input_file}")
    print(f"   출력: {output_dir}")
    print()
    
    # 1. 강의안 파싱
    print("📖 1단계: 강의안 파싱...")
    parser = LectureParser()
    lecture = parser.parse(str(input_file))
    print(f"   ✅ {lecture.title}")
    print(f"   ✅ {len(lecture.sections)}개 섹션 발견")
    print()
    
    # 2. 개요 생성
    print("🔄 2단계: 이중언어 개요 생성 (Gemini API)...")
    generator = OutlineGenerator()
    outlines = []
    
    for section in lecture.sections:
        print(f"   섹션 {section.number}: {section.title}...", end=" ")
        outline = generator.generate_section_outline(section)
        outlines.append(outline)
        print("✅")
    
    # 개요 저장
    outline_file = output_dir / "outline.json"
    with open(outline_file, "w", encoding="utf-8") as f:
        json.dump(outlines, f, ensure_ascii=False, indent=2)
    print(f"   💾 개요 저장: {outline_file}")
    print()
    
    # 3. 슬라이드 생성
    print("🎨 3단계: 슬라이드 생성 (SVG → PNG)...")
    slide_gen = SlideGenerator()
    slides = slide_gen.generate(outlines, lecture_title=lecture.title)
    saved = slide_gen.save_slides(slides, str(output_dir))
    print(f"   ✅ {len(slides)}개 슬라이드 생성")
    print()
    
    # 4. TTS용 텍스트 생성
    print("📝 4단계: TTS용 텍스트 준비...")
    for section in lecture.sections:
        tts_file = output_dir / f"tts_{section.number:02d}.txt"
        # 소제목 제거하고 본문만 추출
        content = section.content.strip()
        tts_file.write_text(content, encoding="utf-8")
    print(f"   ✅ TTS 텍스트 {len(lecture.sections)}개 저장")
    print()
    
    print("=" * 60)
    print("🎉 생성 완료!")
    print(f"   📁 출력 폴더: {output_dir}")
    print()
    print("다음 단계:")
    print(f"   1. TTS 생성: python pipeline.py tts {input_file}")
    print(f"   2. 영상 조립: python pipeline.py assemble {output_dir}")


def cmd_tts(args):
    """TTS 생성 (Gemini API)"""
    input_file = Path(args.input)
    output_dir = Path(args.output) if args.output else OUTPUT_DIR / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔊 Lecture Video Generator: TTS")
    print(f"   입력: {input_file}")
    print(f"   출력: {output_dir}")
    print()
    
    # Import TTS modules
    from modules.tts_generator import TTSGenerator
    
    # 강의안 파싱
    print("📖 강의안 파싱...")
    parser = LectureParser()
    lecture = parser.parse(str(input_file))
    print(f"   ✅ {lecture.title}")
    print(f"   ✅ {len(lecture.sections)}개 섹션")
    print()
    
    # TTS 생성
    print("🔊 TTS 생성 시작 (Gemini API)...")
    generator = TTSGenerator()
    results = generator.generate_for_lecture(lecture, str(output_dir), parallel_workers=1)
    
    print()
    print("=" * 60)
    print(f"🎉 TTS 생성 완료!")
    print(f"   📁 출력 폴더: {output_dir}")
    print(f"   🔊 생성된 오디오: {len(results)}개")
    print()
    print("다음 단계:")
    print(f"   python pipeline.py assemble {output_dir}")


def cmd_assemble(args):
    """영상 조립 (FFmpeg)"""
    input_path = Path(args.input)
    
    # 입력이 파일이면 출력 폴더로 변환 (lecture_video_generator/input/7-4.docx -> output/7-4)
    if input_path.is_file():
        input_dir = OUTPUT_DIR / input_path.stem
    else:
        input_dir = input_path
        
    output_file = args.output if args.output else str(input_dir / "final.mp4")
    
    print(f"🎬 Lecture Video Generator: assemble")
    print(f"   입력: {input_dir}")
    print(f"   출력: {output_file}")
    print(f"   옵션: Fade={not args.no_fade}, Subtitles={not args.no_subtitle}")
    print()
    
    # 1. 자막 생성 (SubtitleGenerator)
    if not args.no_subtitle:
        from modules.subtitle_generator import SubtitleGenerator
        print("📝 자막 생성 중...")
        fade_enabled = not args.no_fade
        transition_overlap = 1.0 if fade_enabled else 0.0
        
        sub_gen = SubtitleGenerator()
        sub_file = sub_gen.generate(
            tts_dir=str(input_dir),
            audio_dir=str(input_dir),
            output_path=str(Path(output_file).with_suffix(".srt")),
            transition_overlap=transition_overlap
        )
        print()
    
    # 2. 영상 조립 (VideoAssembler)
    from modules.video_assembler import VideoAssembler
    
    assembler = VideoAssembler()
    result = assembler.assemble(
        slides_dir=str(input_dir),
        output_file=output_file,
        use_fade=not args.no_fade,
        fade_duration=1.0
    )
    
    if result:
        print()
        print("=" * 60)
        print("🎉 영상 생성 완료!")
        print(f"   📹 출력: {result}")
        if not args.no_subtitle and sub_file:
            print(f"   📜 자막: {sub_file}")
        print()
        print("YouTube 업로드 준비 완료!")
    else:
        print()
        print("❌ 영상 생성 실패")


def cmd_all(args):
    """전체 파이프라인"""
    cmd_generate(args)
    cmd_tts(args)
    cmd_assemble(args)


def main():
    parser = argparse.ArgumentParser(
        description="Lecture Video Generator Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  generate  강의안 → 개요 + 슬라이드 생성
  tts       텍스트 → TTS 음성 생성
  assemble  슬라이드 + 오디오 → 영상 조립
  all       전체 파이프라인 실행

Examples:
  python pipeline.py generate input/lecture.md
  python pipeline.py tts input/lecture.md
  python pipeline.py assemble output/lecture/
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # generate
    gen_parser = subparsers.add_parser("generate", help="개요 + 슬라이드 생성")
    gen_parser.add_argument("input", help="입력 파일 (MD/DOCX)")
    gen_parser.add_argument("-o", "--output", help="출력 폴더")
    gen_parser.set_defaults(func=cmd_generate)
    
    # tts
    tts_parser = subparsers.add_parser("tts", help="TTS 생성")
    tts_parser.add_argument("input", help="입력 파일/폴더")
    tts_parser.add_argument("-o", "--output", help="출력 폴더")
    tts_parser.set_defaults(func=cmd_tts)
    
    # assemble
    asm_parser = subparsers.add_parser("assemble", help="영상 조립")
    asm_parser.add_argument("input", help="입력 폴더 또는 강의안 파일")
    asm_parser.add_argument("-o", "--output", help="출력 파일")
    asm_parser.add_argument("--no-fade", action="store_true", help="페이드 효과 끄기")
    asm_parser.add_argument("--subtitle", action="store_true", help="자막 생성 켜기 (기본값: 꺼짐)")
    asm_parser.set_defaults(no_subtitle=True) # 기본값: 자막 생성 안함
    asm_parser.set_defaults(func=cmd_assemble)
    
    # all
    all_parser = subparsers.add_parser("all", help="전체 파이프라인")
    all_parser.add_argument("input", help="입력 파일")
    all_parser.add_argument("-o", "--output", help="출력 폴더")
    all_parser.add_argument("--no-fade", action="store_true", help="페이드 효과 끄기")
    all_parser.add_argument("--subtitle", action="store_true", help="자막 생성 켜기 (기본값: 꺼짐)")
    all_parser.set_defaults(no_subtitle=True) # 기본값: 자막 생성 안함
    all_parser.set_defaults(func=cmd_all)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
