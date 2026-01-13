#!/usr/bin/env python3
"""
Theological Research Session (Phase 0)
theological_research_v1.3 프롬프트를 Gemini에서 실행하는 브라우저 에이전트

다단계 프로세스:
    1단계: 연구 범위 명료화 → 입력 확인서
    2단계: 범위 견적 → 승인
    3단계: 리서치 기획 → 계획서 승인
    4단계: 자율 리서치 실행
    5단계: Red Team Challenge (QA)
    6단계: Nash Equilibrium Synthesis
    7단계: 최종 결과물

사용법:
    python theological_research_session.py "셰키나"
"""

import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import os

from playwright.async_api import async_playwright


class TheologicalResearchSession:
    """Theological Research v1.3 브라우저 세션"""
    
    AI_STUDIO_URL = "https://aistudio.google.com/prompts/new_chat"
    PROMPTS_DIR = Path(__file__).parent / "prompts"
    OUTPUTS_DIR = Path(os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MS_Brain/300 Tech/320 Coding/Projects.nosync/theological_research/research_outputs"))
    PROFILES_DIR = Path(__file__).parent / ".profiles"
    
    def __init__(self, topic: str):
        self.topic = topic
        self.profile = "account1"  # 유료 계정 고정
        
        # 디렉토리
        self.outputs_dir = self.OUTPUTS_DIR
        self.outputs_dir.mkdir(exist_ok=True)
        self.profiles_dir = self.PROFILES_DIR
        self.profiles_dir.mkdir(exist_ok=True)
        self.user_data_dir = self.profiles_dir / self.profile
        self.user_data_dir.mkdir(exist_ok=True)
        
        # 파일
        self.prompt_file = self.PROMPTS_DIR / "theological_research.md"
        self.output_file = self.outputs_dir / f"{self.topic}_research.md"
        
        print(f"📋 주제: {self.topic}")
        print(f"📁 프로필: {self.profile}")
    
    def load_prompt(self) -> str:
        """theological_research.md 프롬프트 로드 및 주제 삽입"""
        if self.prompt_file.exists():
            content = self.prompt_file.read_text(encoding='utf-8')
            # {{.Input}} 치환
            return content.replace("{{.Input}}", self.topic)
        else:
            print(f"❌ 프롬프트 파일을 찾을 수 없습니다: {self.prompt_file}")
            sys.exit(1)
    
    def copy_to_clipboard(self, text: str):
        """클립보드에 복사 (macOS)"""
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        except:
            return False
    
    def get_from_clipboard(self) -> str:
        """클립보드에서 가져오기 (macOS)"""
        try:
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    async def run(self):
        """다단계 세션 실행"""
        print()
        print("=" * 60)
        print("Theological Research Session (Phase 0)")
        print("Protocol: Adversarial Rationality Game v1.3")
        print("=" * 60)
        print()
        print("📌 7단계 프로세스:")
        print("   1. 연구 범위 명료화")
        print("   2. 범위 견적")
        print("   3. 리서치 기획")
        print("   4. 자율 리서치 실행")
        print("   5. Red Team Challenge")
        print("   6. Nash Equilibrium Synthesis")
        print("   7. 최종 결과물")
        print()
        
        # 프롬프트 로드
        prompt = self.load_prompt()
        print(f"✅ 프롬프트 로드 완료 ({len(prompt):,} 문자)")
        
        async with async_playwright() as p:
            # 브라우저 시작
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = context.pages[0] if context.pages else await context.new_page()
            
            print("🌐 브라우저 시작...")
            
            # Gemini 접속
            try:
                await page.goto(self.AI_STUDIO_URL, wait_until="domcontentloaded", timeout=60000)
            except:
                print("    ⚠ 페이지 로딩 지연, 재시도...")
                await asyncio.sleep(5)
            
            await asyncio.sleep(3)
            
            # ========== 초기 프롬프트 입력 ==========
            print()
            print("┌" + "─" * 58 + "┐")
            print("│  PHASE 0: Theological Research                           │")
            print("│  Protocol: Adversarial Rationality v1.3                  │")
            print("└" + "─" * 58 + "┘")
            print()
            
            # 프롬프트 클립보드 복사
            self.copy_to_clipboard(prompt)
            print("✅ 프롬프트가 클립보드에 복사되었습니다!")
            print()
            print("📝 작업 (AI Studio):")
            print("   1. 채팅창에 붙여넣기 (Cmd+V) → 전송")
            print("   2. 각 단계마다 지시에 따라 응답")
            print("   3. 최종 결과물 완료 시:")
            print("      → 전체 선택 (Cmd+A) → 복사 (Cmd+C)")
            print()
            print("-" * 60)
            input("⏳ 최종 결과물 복사 후 Enter...")
            print("-" * 60)
            
            # 클립보드에서 가져오기
            result_content = self.get_from_clipboard()
            
            if not result_content or len(result_content) < 1000:
                print("\n⚠️ 클립보드에 내용이 없거나 너무 짧습니다.")
                input("   다시 복사 후 Enter...")
                result_content = self.get_from_clipboard()
            
            # 저장
            markdown = self._format_output(result_content)
            self.output_file.write_text(markdown, encoding='utf-8')
            
            await context.close()
        
        # ========== 완료 ==========
        print()
        print("=" * 60)
        print("✅ Theological Research 완료!")
        print("=" * 60)
        print(f"📄 결과물: {self.output_file}")
        print(f"📊 크기: {len(markdown):,} 문자")
        print()
        print("다음 단계 옵션:")
        print(f"   Option A: Phase 1.5 - ./run_depth_enhance.sh {self.topic}")
        print(f"   Option B: Phase 3  - ./run.sh account3 {self.topic}")
    
    def _format_output(self, content: str) -> str:
        """결과물 포맷팅"""
        lines = [
            f"# Theological Research Report",
            f"",
            f"**Topic:** {self.topic}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Protocol:** Adversarial Rationality v1.3 (Nash Equilibrium)",
            f"",
            f"---",
            f"",
            content.strip()
        ]
        return '\n'.join(lines)


async def main():
    if len(sys.argv) < 2:
        print("사용법: python theological_research_session.py [주제]")
        print("예시: python theological_research_session.py 셰키나")
        sys.exit(1)
    
    topic = sys.argv[1]
    session = TheologicalResearchSession(topic)
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
