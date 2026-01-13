#!/usr/bin/env python3
"""
MLA 인용만 남기는 후처리 스크립트
APA, ISO 690 형식의 인용을 제거합니다.
"""

import re
import sys
from pathlib import Path


def clean_citations_mla_only(content: str) -> str:
    """APA, ISO 690 인용을 제거하고 MLA 인용만 남깁니다."""
    lines = content.split('\n')
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # "APA" 라벨 라인 감지 - 이 줄과 다음 인용 줄 제거
        if line.strip() == 'APA':
            i += 1  # APA 라벨 스킵
            # 다음 줄(실제 인용)도 스킵
            if i < len(lines):
                i += 1
            # 빈 줄도 스킵
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        
        # "ISO 690" 라벨 라인 감지
        if line.strip() == 'ISO 690':
            i += 1  # ISO 690 라벨 스킵
            # 다음 줄(실제 인용)도 스킵
            if i < len(lines):
                i += 1
            # 빈 줄도 스킵
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        
        # "> MLA" 라인은 그냥 "> " 로 변경 (라벨 제거)
        if line.strip() == '> MLA':
            cleaned_lines.append('>')
            i += 1
            continue
        
        cleaned_lines.append(line)
        i += 1
    
    return '\n'.join(cleaned_lines)


def process_file(filepath: Path):
    """파일을 처리합니다."""
    print(f"📄 처리 중: {filepath}")
    
    content = filepath.read_text(encoding='utf-8')
    original_lines = len(content.split('\n'))
    
    cleaned = clean_citations_mla_only(content)
    cleaned_lines = len(cleaned.split('\n'))
    
    # 원본 백업
    backup_path = filepath.with_suffix('.md.bak')
    if backup_path.exists():
        backup_path.unlink()  # 기존 백업 삭제
    
    # 현재 파일을 백업으로 복사
    backup_path.write_text(content, encoding='utf-8')
    print(f"   💾 백업: {backup_path}")
    
    # 정제된 내용 저장
    filepath.write_text(cleaned, encoding='utf-8')
    
    removed = original_lines - cleaned_lines
    print(f"   ✅ 완료: {removed}줄 제거 (APA/ISO 690 인용)")
    print(f"   📄 결과: {filepath}")


def main():
    if len(sys.argv) < 2:
        # 기본: results 폴더의 모든 .md 파일 처리
        results_dir = Path(__file__).parent / "results"
        files = [f for f in results_dir.glob("*.md") if not f.name.endswith('.bak')]
        
        if not files:
            print("처리할 .md 파일이 없습니다.")
            return
        
        print(f"🔍 {len(files)}개 파일 발견\n")
        for f in files:
            process_file(f)
            print()
    else:
        # 지정된 파일 처리
        filepath = Path(sys.argv[1])
        if filepath.exists():
            process_file(filepath)
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {filepath}")


if __name__ == "__main__":
    print("=" * 50)
    print("MLA 인용 정제 스크립트")
    print("APA, ISO 690 형식 제거")
    print("=" * 50)
    print()
    main()
