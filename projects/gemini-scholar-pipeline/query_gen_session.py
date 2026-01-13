#!/usr/bin/env python3
"""
Query Generation Session (Phase 2 Only)
기존 .md 리포트에서 시맨틱 검색 질문만 생성

사용법:
    python query_gen_session.py [topic_name]
    
입력: reports/{topic}_raw.md
출력: query.txt
"""

import asyncio
import re
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright


class QueryGenSession:
    """질문 생성 전용 세션 (Phase 2 Only)"""
    
    GEMINI_URL = "https://gemini.google.com"
    REPORTS_DIR = Path(__file__).parent / "reports"
    PROMPTS_DIR = Path(__file__).parent / "prompts"
    PROFILES_DIR = Path(__file__).parent / ".profiles"
    
    def __init__(self, topic: str):
        self.topic = topic
        self.profile = "account1"  # 유료 계정 고정
        
        # 파일 경로
        self.report_file = self.REPORTS_DIR / f"{topic}_raw.md"
        self.query_prompt_file = self.PROMPTS_DIR / "analysis_prompt.md"
        self.query_file = Path(__file__).parent / "query.txt"
        
        # 브라우저 프로필
        self.user_data_dir = self.PROFILES_DIR / self.profile
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📋 주제: {topic}")
        print(f"📄 입력 리포트: {self.report_file}")
    
    def load_report(self) -> str:
        """리포트 파일 로드"""
        if not self.report_file.exists():
            raise FileNotFoundError(f"리포트 파일 없음: {self.report_file}")
        return self.report_file.read_text(encoding='utf-8')
    
    def load_query_prompt(self) -> str:
        """시맨틱 검색 질문 생성 프롬프트 로드"""
        if not self.query_prompt_file.exists():
            raise FileNotFoundError(f"프롬프트 파일 없음: {self.query_prompt_file}")
        return self.query_prompt_file.read_text(encoding='utf-8')
    
    def copy_to_clipboard(self, text: str) -> bool:
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
    
    def _extract_questions_only(self, raw_text: str) -> str:
        """이중언어 질문 추출 (English & German)"""
        result_lines = []
        
        # Q[n] (English) 및 Q[n] (German) 패턴 매칭
        # 예: **Q1 (English):** Question...
        #     **Q1 (German):** Question...
        
        # 1. Q 번호별로 블록 분리
        blocks = re.split(r'\n(?=\*?\*?Q\d+)', raw_text)
        
        for block in blocks:
            # Q 번호 추출
            num_match = re.search(r'Q(\d+)', block)
            if not num_match:
                continue
            
            num = num_match.group(1)
            
            # English 질문 추출
            eng_match = re.search(r'Q\d+\s*\(English\)[*:]*\s*(.+?)(?=\n|$)', block)
            if eng_match:
                q_eng = eng_match.group(1).strip()
                result_lines.append(f"**Q{num} (English):** {q_eng}")
                result_lines.append("")
                
            # German 질문 추출
            ger_match = re.search(r'Q\d+\s*\(German\)[*:]*\s*(.+?)(?=\n|$)', block)
            if ger_match:
                q_ger = ger_match.group(1).strip()
                result_lines.append(f"**Q{num} (German):** {q_ger}")
                result_lines.append("")

            # 기존 단일 포맷 지원 (하위 호환성)
            if not eng_match and not ger_match:
                simple_match = re.search(r'Q\d+\*?\*?:?\s*(.+?)(?=\n|$)', block)
                if simple_match:
                     # 한국어/Target Intent 제거 로직 (기존과 동일)
                    q = simple_match.group(1).strip()
                    if '\n' in q: q = q.split('\n')[0].strip()
                    korean_match = re.search(r'[\uac00-\ud7af]', q)
                    if korean_match: q = q[:korean_match.start()].strip()
                    q = re.split(r'\s*\*?\(?\*?Korean', q)[0].strip()
                    q = re.split(r'\s*\*?Target Intent', q, flags=re.IGNORECASE)[0].strip()
                    
                    if len(q) > 10:
                        result_lines.append(f"**Q{num}:** {q}")
                        result_lines.append("")
        
        return '\n'.join(result_lines)
    
    async def run(self):
        """질문 생성 세션 실행"""
        print()
        print("=" * 60)
        print("Query Generation Session (Phase 2 Only)")
        print("=" * 60)
        print()
        
        # 파일 로드
        try:
            report_content = self.load_report()
            query_prompt = self.load_query_prompt()
            print(f"   ✓ 리포트: {len(report_content):,} 문자")
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return
        
        # 프롬프트 조합
        full_prompt = query_prompt.replace(
            "[여기에 분석할 텍스트나 챕터 내용을 붙여넣으세요]",
            report_content
        )
        print(f"   ✓ 프롬프트 생성: {len(full_prompt):,} 문자")
        
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = context.pages[0] if context.pages else await context.new_page()
            
            print("\n🌐 브라우저 시작...")
            
            try:
                await page.goto(self.GEMINI_URL, wait_until="domcontentloaded", timeout=60000)
            except:
                print("    ⚠ 페이지 로딩 지연...")
            
            await asyncio.sleep(3)
            
            # 클립보드에 프롬프트 복사
            if self.copy_to_clipboard(full_prompt):
                print("✅ 프롬프트가 클립보드에 복사되었습니다!")
            
            print()
            print("┌" + "─" * 58 + "┐")
            print("│  PHASE 2: Query Generation                               │")
            print("└" + "─" * 58 + "┘")
            print()
            print("📝 작업 순서:")
            print("   1. Gemini에서 새 대화를 시작하세요")
            print("   2. 클립보드 내용을 붙여넣기 (Cmd+V)")
            print("   3. 전송 후 질문 생성 대기")
            print("   4. 결과를 복사 (Cmd+C)")
            print("   5. 터미널로 돌아와 Enter")
            print()
            print("-" * 60)
            input("⏳ 질문 복사 후 Enter를 눌러주세요...")
            print("-" * 60)
            
            await context.close()
        
        # 질문 추출 및 저장
        raw_response = self.get_from_clipboard()
        
        if raw_response and ('Q1' in raw_response or '**Q1' in raw_response):
            cleaned_questions = self._extract_questions_only(raw_response)
            self.query_file.write_text(cleaned_questions, encoding='utf-8')
            q_count = len(re.findall(r'\*?\*?Q\d+', cleaned_questions))
            
            print()
            print("=" * 60)
            print("✅ Phase 2 완료!")
            print("=" * 60)
            print(f"📄 저장: {self.query_file}")
            print(f"📊 질문: {q_count}개 (영어만 추출)")
            print()
            print("다음 단계:")
            print(f"   ./run.sh account3 {self.topic}")
        else:
            print("\n⚠️ 질문 형식이 감지되지 않았습니다.")
            print("   query.txt를 직접 편집해 주세요.")


async def main():
    if len(sys.argv) < 2:
        print("사용법: python query_gen_session.py [topic_name]")
        print()
        print("📌 리포트 파일이 다음 위치에 있어야 합니다:")
        print("   reports/{topic_name}_raw.md")
        sys.exit(1)
    
    topic = sys.argv[1]
    session = QueryGenSession(topic)
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
