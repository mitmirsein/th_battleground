#!/usr/bin/env python3
"""
Footnote Integration Session (Phase 4) - JSON Mapping Mode
Gemini가 JSON 매핑을 생성하면, 이 스크립트가 원본에 각주를 삽입합니다.

사용법:
    python integration_session.py [topic_name]
"""

import asyncio
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


class IntegrationSession:
    """각주 통합 세션 - JSON 매핑 방식"""
    
    GEMINI_URL = "https://gemini.google.com"
    REPORTS_DIR = Path(__file__).parent / "reports"
    RESULTS_DIR = Path(__file__).parent / "results"
    PROMPTS_DIR = Path(__file__).parent / "prompts"
    PROFILES_DIR = Path(__file__).parent / ".profiles"
    
    def __init__(self, topic: str):
        self.topic = topic
        self.profile = "account1"
        
        # 파일 경로
        self.report_file = self.REPORTS_DIR / f"{topic}_raw.md"
        self.scholar_file = self.RESULTS_DIR / f"{topic}.md"
        self.prompt_file = self.PROMPTS_DIR / "integration_prompt.md"
        self.output_file = self.REPORTS_DIR / f"{topic}_annotated.md"
        self.mapping_file = self.REPORTS_DIR / f"{topic}_footnotes.json"
        
        # 브라우저 프로필
        self.user_data_dir = self.PROFILES_DIR / self.profile
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📋 주제: {topic}")
        print(f"📄 Gemini 리포트: {self.report_file}")
        print(f"📚 Scholar 결과: {self.scholar_file}")
    
    def load_files(self) -> tuple[str, str, str]:
        """필요한 파일들 로드"""
        if not self.report_file.exists():
            raise FileNotFoundError(f"리포트 파일 없음: {self.report_file}")
        
        if not self.scholar_file.exists():
            raise FileNotFoundError(f"Scholar 결과 없음: {self.scholar_file}")
        
        if not self.prompt_file.exists():
            raise FileNotFoundError(f"프롬프트 파일 없음: {self.prompt_file}")
        
        report = self.report_file.read_text(encoding='utf-8')
        scholar = self.scholar_file.read_text(encoding='utf-8')
        prompt = self.prompt_file.read_text(encoding='utf-8')
        
        print(f"   ✓ 리포트: {len(report):,} 문자")
        print(f"   ✓ Scholar: {len(scholar):,} 문자")
        
        return report, scholar, prompt
    
    def build_full_prompt(self, report: str, scholar: str, prompt_template: str) -> str:
        """전체 프롬프트 조합"""
        full_prompt = prompt_template.replace(
            "[여기에 Gemini 리포트 내용이 삽입됩니다]",
            report
        )
        full_prompt = full_prompt.replace(
            "[여기에 Scholar 인용 목록이 삽입됩니다]",
            scholar
        )
        return full_prompt
    
    def copy_to_clipboard(self, text: str) -> bool:
        """클립보드에 복사"""
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        except:
            return False
    
    def get_from_clipboard(self) -> str:
        """클립보드에서 읽기"""
        try:
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    def parse_json_response(self, raw_response: str) -> dict:
        """Gemini 응답에서 JSON 추출"""
        # 마크다운 코드블록 제거
        content = raw_response.strip()
        if '```json' in content:
            content = content.split('```json')[1]
        if '```' in content:
            content = content.split('```')[0]
        
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 파싱 오류: {e}")
            # 부분 추출 시도
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return None
    
    def apply_footnotes(self, report: str, mapping: dict) -> str:
        """원본 리포트에 각주 삽입 (Anchor System 지원)"""
        footnotes = mapping.get('footnotes', [])
        source_comparison = mapping.get('source_comparison', [])
        bibliography = mapping.get('bibliography', [])
        
        result = report
        inserted_count = 0
        
        # 각주 삽입 (역순으로 처리하여 위치 변경 방지)
        for fn in sorted(footnotes, key=lambda x: x['id'], reverse=True):
            target = fn.get('target_text', '')
            anchor_before = fn.get('anchor_before', '')
            fn_id = fn['id']
            
            if not target:
                continue
            
            # Anchor System: anchor_before + target_text 조합으로 정확한 위치 찾기
            if anchor_before:
                search_pattern = anchor_before + target
                if search_pattern in result:
                    result = result.replace(
                        search_pattern,
                        f"{anchor_before}{target}[^{fn_id}]",
                        1
                    )
                    inserted_count += 1
                    continue
            
            # Fallback: target_text만으로 매칭
            if target in result:
                result = result.replace(target, f"{target}[^{fn_id}]", 1)
                inserted_count += 1
        
        print(f"   ✓ {inserted_count}/{len(footnotes)} 각주 삽입 완료")
        
        # 미주 섹션 추가 (Chicago Footnote 형식)
        result += "\n\n---\n\n## Endnotes\n\n"
        
        for fn in footnotes:
            # citation_chicago 우선, 없으면 citation_mla 사용
            citation = fn.get('citation_chicago', fn.get('citation_mla', ''))
            result += f"[^{fn['id']}]: {citation}\n\n"
        
        # Bibliography 섹션 (성, 이름 순서)
        if bibliography:
            result += "\n---\n\n## Bibliography\n\n"
            for bib in bibliography:
                result += f"- {bib}\n"
        
        # 출처 비교 테이블
        if source_comparison:
            result += "\n---\n\n## Source Comparison\n\n"
            result += "| Original (Web) | Academic Replacement | Status |\n"
            result += "|----------------|---------------------|--------|\n"
            
            for item in source_comparison:
                orig = item.get('original_web', item.get('original', '-'))
                repl = item.get('academic_replacement', item.get('replacement', '-'))
                status = "🟢 Replaced" if item.get('status') == 'replaced' else "🔴 No match"
                result += f"| {orig} | {repl} | {status} |\n"
        
        # 메타데이터 헤더 추가
        header = f"""---
title: "{self.topic} (Annotated)"
generated: "{datetime.now().strftime('%Y-%m-%d %H:%M')}"
source_report: "{self.report_file.name}"
scholar_results: "{self.scholar_file.name}"
footnote_count: {len(footnotes)}
---

"""
        return header + result
    
    async def run(self):
        """통합 세션 실행"""
        print()
        print("=" * 60)
        print("Footnote Integration Session (Phase 4)")
        print("=" * 60)
        print()
        
        # 파일 로드
        try:
            report, scholar, prompt_template = self.load_files()
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return
        
        # 프롬프트 조합
        full_prompt = self.build_full_prompt(report, scholar, prompt_template)
        print(f"\n📝 프롬프트 생성 완료 ({len(full_prompt):,} 문자)")
        
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
            print("│  PHASE 4: Footnote Mapping Generation                    │")
            print("└" + "─" * 58 + "┘")
            print()
            print("📝 작업 순서:")
            print("   1. Gemini에 새 대화를 시작하세요")
            print("   2. 클립보드 내용을 붙여넣기 (Cmd+V)")
            print("   3. 전송 후 JSON 결과 생성 대기")
            print("   4. JSON 결과를 복사 (Cmd+A → Cmd+C)")
            print("   5. 터미널로 돌아와 Enter")
            print()
            print("💡 출력은 JSON 형식입니다 (각주 매핑 정보)")
            print()
            print("-" * 60)
            input("⏳ JSON 복사 후 Enter를 눌러주세요...")
            print("-" * 60)
            
            await context.close()
        
        # JSON 파싱
        raw_response = self.get_from_clipboard()
        mapping = self.parse_json_response(raw_response)
        
        if mapping:
            # JSON 저장
            self.mapping_file.write_text(
                json.dumps(mapping, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            print(f"\n📄 매핑 저장: {self.mapping_file}")
            
            # 각주 삽입
            print("\n🔧 각주 삽입 중...")
            annotated = self.apply_footnotes(report, mapping)
            self.output_file.write_text(annotated, encoding='utf-8')
            
            # 통계
            fn_count = len(mapping.get('footnotes', []))
            src_count = len(mapping.get('source_comparison', []))
            
            print()
            print("=" * 60)
            print("✅ Phase 4 완료!")
            print("=" * 60)
            print(f"📄 출력 파일: {self.output_file}")
            print(f"📊 원본 크기: {len(report):,} 문자")
            print(f"📊 결과 크기: {len(annotated):,} 문자")
            print(f"📝 각주 수: {fn_count}개")
            print(f"📊 출처 비교: {src_count}개")
        else:
            print("\n⚠️ JSON을 파싱할 수 없습니다.")
            print("   결과를 다시 확인해 주세요.")


async def main():
    if len(sys.argv) < 2:
        print("사용법: python integration_session.py [topic_name]")
        sys.exit(1)
    
    topic = sys.argv[1]
    session = IntegrationSession(topic)
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
