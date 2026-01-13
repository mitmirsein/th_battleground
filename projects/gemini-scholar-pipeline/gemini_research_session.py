#!/usr/bin/env python3
"""
Gemini Research Agent (Phase 1 + 2 통합)
Gemini Deep Research 수행 후 → 시맨틱 검색 질문 생성까지 한 세션에서 처리

사용법:
    python gemini_research_session.py [topic_name]
"""

import asyncio
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


class GeminiResearchSession:
    """Gemini Deep Research + Query Generation 통합 세션"""
    
    GEMINI_URL = "https://gemini.google.com"
    REPORTS_DIR = Path(__file__).parent / "reports"
    PROMPTS_DIR = Path(__file__).parent / "prompts"
    PROFILES_DIR = Path(__file__).parent / ".profiles"
    
    def __init__(self, topic: str = None):
        self.topic = topic or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.profile = "account1"  # 유료 계정 고정
        
        # 디렉토리
        self.reports_dir = self.REPORTS_DIR
        self.reports_dir.mkdir(exist_ok=True)
        self.profiles_dir = self.PROFILES_DIR
        self.profiles_dir.mkdir(exist_ok=True)
        self.user_data_dir = self.profiles_dir / self.profile
        self.user_data_dir.mkdir(exist_ok=True)
        
        # 파일
        self.report_file = self.reports_dir / f"{self.topic}_raw.md"
        self.query_prompt_file = self.PROMPTS_DIR / "analysis_prompt.md"
        self.query_file = Path(__file__).parent / "query.txt"
        
        print(f"📋 주제: {self.topic}")
        print(f"📁 프로필: {self.profile}")
    
    def load_query_prompt(self) -> str:
        """시맨틱 검색 질문 생성 프롬프트 로드"""
        if self.query_prompt_file.exists():
            return self.query_prompt_file.read_text(encoding='utf-8')
        return ""
    
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
        """통합 세션 실행"""
        print()
        print("=" * 60)
        print("Gemini Research Session (Phase 1 + 2)")
        print("=" * 60)
        print()
        print("📌 이 세션에서 수행할 작업:")
        print("   1. Gemini Deep Research 수행")
        print("   2. 연구 결과 저장")
        print("   3. 시맨틱 검색용 질문 생성")
        print()
        
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
                await page.goto(self.GEMINI_URL, wait_until="domcontentloaded", timeout=60000)
            except:
                print("    ⚠ 페이지 로딩 지연, 재시도...")
                await asyncio.sleep(5)
            
            await asyncio.sleep(3)
            
            # ========== PHASE 1: Deep Research ==========
            print()
            print("┌" + "─" * 58 + "┐")
            print("│  PHASE 1: Deep Research                                  │")
            print("└" + "─" * 58 + "┘")
            print()
            print("📝 작업:")
            print("   1. Gemini에서 연구 주제를 입력하세요")
            print("   2. 'Deep Research' 모드를 활성화하세요")
            print("   3. 연구 계획을 검토하고 '연구 시작'을 클릭하세요")
            print("   4. 연구가 완료되면:")
            print("      → 'Google Docs로 내보내기' 클릭")
            print("      → Google Docs에서 Cmd+A → Cmd+C")
            print()
            print("💡 Google Docs 내보내기 = 마크다운 구조 + 각주 + References 보존")
            print()
            print("-" * 60)
            input("⏳ Google Docs에서 복사 후 Enter...")
            print("-" * 60)
            
            # 클립보드에서 가져오기
            report_content = self.get_from_clipboard()
            
            if not report_content or len(report_content) < 500:
                print("\n⚠️ 클립보드에 내용이 없거나 너무 짧습니다.")
                input("   다시 복사 후 Enter...")
                report_content = self.get_from_clipboard()
            
            markdown = self._format_report(report_content)
            self.report_file.write_text(markdown, encoding='utf-8')
            print(f"\n✅ Phase 1 완료!")
            print(f"   📄 저장: {self.report_file}")
            print(f"   📊 크기: {len(markdown):,} 문자")
            
            # ========== PHASE 2: Query Generation ==========
            print()
            print("┌" + "─" * 58 + "┐")
            print("│  PHASE 2: Query Generation                               │")
            print("└" + "─" * 58 + "┘")
            print()
            
            # 질문 생성 프롬프트 준비
            query_prompt = self.load_query_prompt()
            if query_prompt and report_content:
                # 프롬프트에 리포트 내용 삽입
                full_prompt = query_prompt.replace(
                    "[여기에 분석할 텍스트나 챕터 내용을 붙여넣으세요]",
                    report_content
                )
                
                print("🔄 새 대화 시작 중...")
                
                # 새 대화 버튼 찾기 및 클릭
                try:
                    # 새 채팅 버튼 (다양한 선택자 시도)
                    new_chat_selectors = [
                        'button[aria-label*="새"]',
                        'button[aria-label*="New"]',
                        'a[href="/app"]',
                        '[data-test-id="new-chat"]',
                    ]
                    
                    for selector in new_chat_selectors:
                        try:
                            btn = await page.query_selector(selector)
                            if btn:
                                await btn.click()
                                await asyncio.sleep(2)
                                print("   ✓ 새 대화 시작됨")
                                break
                        except:
                            continue
                except:
                    print("   ⚠ 새 대화 버튼을 찾지 못함 - 수동으로 시작하세요")
                
                await asyncio.sleep(2)
                
                # 입력창 찾기
                print("📝 프롬프트 입력 중...")
                
                input_selectors = [
                    'div[contenteditable="true"]',
                    'textarea',
                    '.ql-editor',
                    '[aria-label*="메시지"]',
                    '[aria-label*="Message"]',
                ]
                
                input_found = False
                for selector in input_selectors:
                    try:
                        input_el = await page.query_selector(selector)
                        if input_el:
                            await input_el.click()
                            await asyncio.sleep(0.5)
                            
                            # 프롬프트 입력 (클립보드 + 붙여넣기)
                            self.copy_to_clipboard(full_prompt)
                            await page.keyboard.press("Meta+v")  # Cmd+V
                            await asyncio.sleep(1)
                            
                            print("   ✓ 프롬프트 입력 완료")
                            input_found = True
                            break
                    except:
                        continue
                
                if not input_found:
                    print("   ⚠ 입력창을 찾지 못함")
                    print("   클립보드에 프롬프트가 복사되었습니다. 수동으로 붙여넣기(Cmd+V)하세요.")
                    self.copy_to_clipboard(full_prompt)
                
                # 전송 버튼 클릭
                await asyncio.sleep(1)
                print("📤 전송 중...")
                
                send_selectors = [
                    'button[aria-label*="보내"]',
                    'button[aria-label*="Send"]',
                    'button[aria-label*="submit"]',
                    'button.send-button',
                    '[data-test-id="send-button"]',
                ]
                
                sent = False
                for selector in send_selectors:
                    try:
                        btn = await page.query_selector(selector)
                        if btn:
                            await btn.click()
                            print("   ✓ 전송됨")
                            sent = True
                            break
                    except:
                        continue
                
                if not sent:
                    # Enter 키로 전송 시도
                    try:
                        await page.keyboard.press("Enter")
                        print("   ✓ Enter로 전송됨")
                        sent = True
                    except:
                        print("   ⚠ 전송 버튼을 찾지 못함 - 수동으로 전송하세요")
                
                print()
                print("-" * 60)
                print("⏳ 응답 생성 완료 후, 결과를 복사(Cmd+C)하고 Enter를 눌러주세요...")
                input()
                print("-" * 60)
                
                # 클립보드에서 질문 가져오기
                questions_raw = self.get_from_clipboard()
                
                if questions_raw and ('Q1' in questions_raw or '**Q1' in questions_raw):
                    # 질문만 추출 (한국어 번역, Target Intent 제거)
                    cleaned_questions = self._extract_questions_only(questions_raw)
                    self.query_file.write_text(cleaned_questions, encoding='utf-8')
                    q_count = len(re.findall(r'\*?\*?Q\d+', cleaned_questions))
                    print(f"\n✅ Phase 2 완료!")
                    print(f"   📄 저장: {self.query_file}")
                    print(f"   📊 질문: {q_count}개 (영어만 추출)")
                else:
                    print("\n⚠️ 질문 형식이 감지되지 않았습니다.")
                    print("   query.txt를 직접 편집해 주세요.")
            
            await context.close()
        
        # ========== 완료 ==========
        print()
        print("=" * 60)
        print("✅ 세션 완료!")
        print("=" * 60)
        print(f"📄 리포트: {self.report_file}")
        print(f"📄 질문: {self.query_file}")
        print()
        print("다음 단계:")
        print(f"   ./run.sh account3 {self.topic}")
    
    def _format_report(self, content: str) -> str:
        """리포트 포맷팅 - 마크다운 구조 복원"""
        # 마크다운 구조 복원
        formatted = self._restore_markdown_structure(content.strip())
        
        lines = [
            f"# Gemini Deep Research Report",
            f"",
            f"**Topic:** {self.topic}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Source:** Gemini Deep Research",
            f"",
            f"---",
            f"",
            formatted
        ]
        return '\n'.join(lines)
    
    def _restore_markdown_structure(self, text: str) -> str:
        """마크다운 구조 복원 - 헤딩 및 문단 구분"""
        import re
        
        result = text
        
        # 1. 주요 섹션 헤딩 (제1부:, 제2부: 등)
        result = re.sub(
            r'(제\d+부:\s*[^\.]+)',
            r'\n\n## \1\n\n',
            result
        )
        
        # 2. 중간 헤딩 (1.1, 2.1 등 - 숫자.숫자 형식)
        result = re.sub(
            r'(\d+\.\d+)\s+([가-힣A-Za-z][^\.]{10,50}?)(?=[가-힣A-Za-z])',
            r'\n\n### \1 \2\n\n',
            result
        )
        
        # 3. 소제목 (1.1.1, 2.1.1 등)
        result = re.sub(
            r'(\d+\.\d+\.\d+)\s+([가-힣A-Za-z][^\n]{5,50}?)(?=[가-힣A-Za-z])',
            r'\n\n#### \1 \2\n\n',
            result
        )
        
        # 4. 서론/결론 헤딩
        result = re.sub(
            r'(서론:\s*[^\n]+)',
            r'\n\n## \1\n\n',
            result
        )
        result = re.sub(
            r'(결론:\s*[^\n]+)',
            r'\n\n## \1\n\n',
            result
        )
        
        # 5. 표 제목 (표 1:, 표 2: 등)
        result = re.sub(
            r'(표\s*\d+:\s*[^\n]+)',
            r'\n\n### \1\n\n',
            result
        )
        
        # 6. 문단 구분 (마침표 후 대문자/한글 시작)
        # 너무 많은 줄바꿈 방지를 위해 선택적 적용
        result = re.sub(
            r'(\.)(\d+\s)',  # 마침표 후 숫자 (각주 번호) 뒤
            r'\1\n\n\2',
            result
        )
        
        # 7. 중복 줄바꿈 정리
        result = re.sub(r'\n{4,}', '\n\n\n', result)
        
        # 8. 헤딩 전후 공백 정리
        result = re.sub(r'\n+(#{2,4})', r'\n\n\1', result)
        result = re.sub(r'(#{2,4}[^\n]+)\n+', r'\1\n\n', result)
        
        return result.strip()
    
    def _extract_questions_only(self, raw_text: str) -> str:
        """이중언어 질문 추출 (English & German)"""
        result_lines = []
        
        # Q[n] (English) 및 Q[n] (German) 패턴 매칭
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

            # 기존 단일 포맷 지원
            if not eng_match and not ger_match:
                simple_match = re.search(r'Q\d+\*?\*?:?\s*(.+?)(?=\n|$)', block)
                if simple_match:
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


async def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    session = GeminiResearchSession(topic)
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
