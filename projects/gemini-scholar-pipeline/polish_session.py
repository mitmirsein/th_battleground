#!/usr/bin/env python3
"""
Phase 5: 문체 개선 세션 (브라우저 에이전틱)
불릿 포인트를 학술 문단으로 변환
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

class PolishSession:
    def __init__(self, topic: str):
        self.topic = topic
        self.annotated_file = Path(f"reports/{topic}_annotated.md")
        self.final_file = Path(f"reports/{topic}_final.md")
        self.prompt_file = Path("prompts/polish_prompt.md")
        self.profile_dir = Path(".profiles/account1")
        
    def copy_to_clipboard(self, text: str):
        """클립보드에 복사 (macOS)"""
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
        
    def get_from_clipboard(self) -> str:
        """클립보드에서 읽기 (macOS)"""
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout
    
    def load_annotated_report(self) -> str:
        """각주가 포함된 리포트 로드"""
        if not self.annotated_file.exists():
            raise FileNotFoundError(f"파일 없음: {self.annotated_file}")
        return self.annotated_file.read_text(encoding='utf-8')
    
    def load_prompt(self) -> str:
        """문체 개선 프롬프트 로드"""
        if not self.prompt_file.exists():
            raise FileNotFoundError(f"프롬프트 없음: {self.prompt_file}")
        return self.prompt_file.read_text(encoding='utf-8')
    
    def build_full_prompt(self) -> str:
        """전체 프롬프트 조합"""
        prompt = self.load_prompt()
        report = self.load_annotated_report()
        
        full_prompt = f"{prompt}\n\n---\n\n{report}"
        return full_prompt
    
    async def run(self):
        """메인 실행"""
        print("\n" + "=" * 60)
        print("  PHASE 5: 문체 개선 (Academic Prose Polish)")
        print("=" * 60)
        
        # 프롬프트 준비
        full_prompt = self.build_full_prompt()
        
        # 임시 파일 저장 (디버깅용)
        Path("temp_polish_prompt.txt").write_text(full_prompt, encoding='utf-8')
        print(f"\n📄 프롬프트 크기: {len(full_prompt):,} 문자")
        
        # 클립보드에 복사
        self.copy_to_clipboard(full_prompt)
        print("📋 프롬프트가 클립보드에 복사되었습니다")
        
        async with async_playwright() as p:
            # 브라우저 실행
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=False,
                viewport={"width": 1400, "height": 900}
            )
            
            page = await browser.new_page()
            await page.goto("https://gemini.google.com")
            await asyncio.sleep(3)
            
            print()
            print("┌" + "─" * 58 + "┐")
            print("│  PHASE 5: 문체 개선                                     │")
            print("└" + "─" * 58 + "┘")
            print()
            print("📝 작업:")
            print("   1. Gemini 입력창에 붙여넣기 (Cmd+V)")
            print("   2. 전송 후 응답 대기")
            print("   3. 응답 전체를 복사 (Cmd+A → Cmd+C)")
            print()
            print("💡 각주 [^n]과 헤딩 ##이 보존되어야 합니다!")
            print()
            print("-" * 60)
            input("⏳ 결과 복사 후 Enter...")
            print("-" * 60)
            
            # 결과 가져오기
            result = self.get_from_clipboard()
            
            if result and len(result) > 1000:
                # 헤더 추가
                header = f"""---
title: "{self.topic} (Final)"
generated: "{datetime.now().strftime('%Y-%m-%d %H:%M')}"
source: "{self.annotated_file.name}"
phase: "5 - Academic Prose Polish"
---

"""
                final_content = header + result
                
                # 저장
                self.final_file.write_text(final_content, encoding='utf-8')
                print(f"\n✅ Phase 5 완료!")
                print(f"   📄 저장: {self.final_file}")
                print(f"   📊 크기: {len(final_content):,} 문자")
                
                # 각주 보존 확인
                footnote_count = result.count("[^")
                print(f"   📎 각주: {footnote_count // 2}개 감지")
            else:
                print("\n⚠️ 결과가 너무 짧습니다. 다시 시도해주세요.")
            
            await browser.close()


async def main():
    import sys
    if len(sys.argv) < 2:
        print("사용법: python polish_session.py <topic>")
        print("예시: python polish_session.py justification")
        sys.exit(1)
    
    topic = sys.argv[1]
    session = PolishSession(topic)
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
