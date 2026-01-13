#!/usr/bin/env python3
"""
Google Scholar Labs 시맨틱 검색 에이전트 (v2)
- 세션 제한 대응: 질문 3개씩 배치 처리
- 누적 저장: 동일 파일에 결과 누적
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


class ScholarLabsAgent:
    """Google Scholar Labs 시맨틱 검색 에이전트"""
    
    SCHOLAR_LABS_URL = "https://scholar.google.com/scholar_labs/search?hl=ko"
    RESULTS_DIR = Path(__file__).parent / "results"
    PROFILES_DIR = Path(__file__).parent / ".profiles"
    BATCH_SIZE = 5  # 세션 제한 대응: 한 세션당 최대 질문 수
    
    def __init__(self, profile: str = "default", job: str = None):
        self.profile = profile
        self.results_dir = self.RESULTS_DIR
        self.results_dir.mkdir(exist_ok=True)
        self.profiles_dir = self.PROFILES_DIR
        self.profiles_dir.mkdir(exist_ok=True)
        
        # 작업(Job) 이름 설정 (기본값: 타임스탬프)
        if job is None:
            job = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.job = job
        
        # 작업별 상태 파일 및 결과 파일
        self.state_file = self.results_dir / f".state_{job}.json"
        self.output_file = self.results_dir / f"{job}.md"
        
        # 프로필별 브라우저 데이터 디렉토리
        self.user_data_dir = self.profiles_dir / profile
        self.user_data_dir.mkdir(exist_ok=True)
        
        print(f"📁 프로필: {profile}")
        print(f"📋 작업명: {job}")
        print(f"📄 결과 파일: {self.output_file}")
    
    def parse_queries(self, raw_input: str) -> list[str]:
        """사용자 입력에서 검색 질문 목록을 파싱합니다."""
        lines = raw_input.strip().split('\n')
        queries = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Q1:, Q2: 형식 또는 1., 2. 형식 제거
            cleaned = re.sub(r'^(Q?\d+[\.:]\s*)', '', line, flags=re.IGNORECASE)
            cleaned = cleaned.strip()
            
            if cleaned:
                queries.append(cleaned)
        
        return queries
    
    def load_state(self) -> dict:
        """이전 검색 상태 로드"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding='utf-8'))
        return {"completed_queries": [], "results": []}
    
    def save_state(self, state: dict):
        """검색 상태 저장"""
        self.state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def clear_state(self):
        """검색 상태 초기화"""
        if self.state_file.exists():
            self.state_file.unlink()
    
    async def search_scholar_labs_fast(self, page, query: str) -> bool:
        """검색 입력 후 결과가 안정화될 때까지 지능형 대기 (AI 분석 시간 고려)
        
        Returns:
            True if results appeared and stabilized, False otherwise
        """
        try:
            # 검색창 찾기
            search_box = None
            selectors = ['textarea#gs_as_i_t', 'textarea[name="q"]', 'textarea', 'input[type="text"]']
            
            for selector in selectors:
                try:
                    search_box = await page.wait_for_selector(selector, timeout=5000)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                return False
            
            await search_box.fill('')
            await search_box.fill(query)
            await search_box.press('Enter')
            print(f"    ✓ 검색 제출")
            
            # 지능형 대기 로직: 결과 개수 안정화 감지
            print(f"    ⏳ AI 분석 및 결과 생성 대기 중 (최대 90초)...")
            
            stable_ticks = 0
            last_count = 0
            max_wait = 90
            
            for i in range(max_wait):
                await asyncio.sleep(1)
                
                # 현재 유효 결과 개수 확인
                all_links = await page.query_selector_all('a[id]')
                current_count = 0
                for link in all_links:
                    try:
                        lid = await link.get_attribute('id')
                        if lid and not lid.startswith('gs_'):
                            current_count += 1
                    except:
                        continue
                
                # 진행 상황 로깅 (3초마다 변경 시에만)
                if i > 0 and i % 3 == 0:
                    # '평가됨' 텍스트 확인 (보조 지표)
                    try:
                        body_text = await page.inner_text('body')
                        status = "분석 중"
                        if '평가됨' in body_text or 'Evaluated' in body_text:
                            status = "평가됨"
                        print(f"       [{i}s] 논문: {current_count}개 ({status})...")
                    except:
                        pass

                # 안정화 체크 로직
                if current_count > 0:
                    if current_count == last_count:
                        stable_ticks += 1
                    else:
                        stable_ticks = 0 # 변화가 있으면 리셋
                    
                    # 5초 연속 변화 없고, 최소 1개 이상이면 완료
                    if stable_ticks >= 5 and current_count >= 1:
                        print(f"    ✓ 결과 안정화 완료 ({current_count}개 수집, {i}초 소요)")
                        return True
                
                last_count = current_count
            
            if last_count > 0:
                print(f"    ⚠ 대기 시간 종료, {last_count}개 결과로 진행")
                return True
            
            print(f"    ⚠ 결과 없음 (Timeout)")
            return False
            
        except Exception as e:
            print(f"    ❌ 검색 제출 오류: {e}")
            return False
    
    async def extract_citations_from_page(self, page, max_results: int = 10) -> list[dict]:
        """현재 페이지에서 인용 정보를 추출 (병렬 실행용)"""
        # 안정화 대기
        await asyncio.sleep(5)
        results = await self._parse_labs_results(page, max_results)
        return results
    
    async def search_scholar_labs(self, page, query: str, max_results: int = 10, is_first_in_batch: bool = False) -> list[dict]:
        """Google Scholar Labs에서 시맨틱 검색을 수행합니다. (레거시 호환)"""
        MAX_RETRY = 2
        results = []
        
        try:
            search_box = None
            selectors = ['textarea#gs_as_i_t', 'textarea[name="q"]', 'textarea', 'input[type="text"]']
            
            for selector in selectors:
                try:
                    search_box = await page.wait_for_selector(selector, timeout=5000)
                    if search_box:
                        print(f"    📝 검색창 발견: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                print("    ❌ 검색창을 찾을 수 없습니다")
                return results
            
            await search_box.fill('')
            await search_box.fill(query)
            await search_box.press('Enter')
            
            # 대기시간 단축 (30/15초)
            wait_time = 30 if is_first_in_batch else 15
            print(f"    ⏳ 결과 로딩 중... (약 {wait_time}초)")
            await asyncio.sleep(wait_time)
            
            try:
                await page.wait_for_selector('text=평가됨', timeout=30000)
                print("    ✓ 평가 완료")
            except:
                print("    ⚠ 평가 확인 실패, 계속...")
            
            await asyncio.sleep(5)
            
            for attempt in range(MAX_RETRY + 1):
                results = await self._parse_labs_results(page, max_results)
                if results:
                    break
                if attempt < MAX_RETRY:
                    print(f"    ⚠ 재시도 {attempt + 1}/{MAX_RETRY}...")
                    await asyncio.sleep(10)
            
        except PlaywrightTimeout:
            print(f"  ⏱ 타임아웃: {query[:50]}...")
        except Exception as e:
            print(f"  ❌ 검색 오류: {e}")
        
        return results
    
    async def _parse_labs_results(self, page, max_results: int) -> list[dict]:
        """Scholar Labs 결과를 파싱합니다."""
        results = []
        
        all_links = await page.query_selector_all('a[id]')
        
        paper_links = []
        for link in all_links:
            link_id = await link.get_attribute('id')
            href = await link.get_attribute('href')
            
            if link_id and href and not link_id.startswith('gs_'):
                try:
                    text = await link.inner_text()
                    if text and len(text) > 10:
                        paper_links.append({'element': link, 'id': link_id, 'href': href, 'title': text})
                except:
                    continue
        
        for i, paper in enumerate(paper_links[:max_results]):
            try:
                result = {
                    'title': paper['title'].strip(),
                    'link': paper['href'],
                }
                
                parent = await paper['element'].evaluate_handle('el => el.parentElement.parentElement')
                parent_text = await parent.evaluate('el => el.innerText')
                lines = parent_text.split('\n')
                
                meta_line = ""
                snippet_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line or line == result['title']:
                        continue
                    if '인용' in line and '회' in line:
                        result['citations'] = line
                    elif re.search(r'\d{4}', line) and len(line) < 150:
                        if not meta_line:
                            meta_line = line
                    else:
                        if len(line) > 20:
                            snippet_lines.append(line)
                
                result['meta'] = meta_line
                result['snippet'] = ' '.join(snippet_lines[:3])
                
                # MLA 인용 추출 시도
                mla_citation = await self._extract_mla_citation(page, paper['element'])
                if mla_citation:
                    result['mla_citation'] = mla_citation
                
                results.append(result)
                
            except Exception as e:
                continue
        
        return results
    
    async def _extract_mla_citation(self, page, paper_element) -> str:
        """인용 버튼을 클릭하여 MLA 형식 인용을 추출합니다."""
        try:
            # 논문 요소의 부모에서 '인용' 링크 찾기
            parent = await paper_element.evaluate_handle('el => el.parentElement.parentElement.parentElement')
            
            # "인용" 또는 "저장" 텍스트가 있는 링크 찾기
            cite_link = await parent.query_selector('a:has-text("인용")')
            
            if not cite_link:
                # 대안: 클래스나 다른 속성으로 찾기
                cite_link = await parent.query_selector('a[aria-label*="인용"]')
            
            if not cite_link:
                return ""
            
            # 인용 링크 클릭
            await cite_link.click()
            await asyncio.sleep(1.5)  # 팝업 로딩 대기
            
            # MLA 형식 텍스트 추출 (팝업에서)
            # Scholar의 인용 팝업은 보통 #gs_cit 또는 유사한 ID를 가짐
            mla_text = ""
            
            # 방법 1: MLA 탭/라벨이 있는 경우
            mla_tab = await page.query_selector('a:has-text("MLA")')
            if mla_tab:
                await mla_tab.click()
                await asyncio.sleep(0.5)
            
            # 방법 2: 인용 텍스트 추출
            citation_box = await page.query_selector('#gs_citt')
            if citation_box:
                mla_text = await citation_box.inner_text()
            else:
                # 대안: 팝업 내 첫 번째 인용 텍스트
                citation_div = await page.query_selector('.gs_citr')
                if citation_div:
                    mla_text = await citation_div.inner_text()
            
            # 팝업 닫기 (ESC 키 또는 닫기 버튼)
            close_btn = await page.query_selector('#gs_cit-x')
            if close_btn:
                await close_btn.click()
            else:
                await page.keyboard.press('Escape')
            
            await asyncio.sleep(0.5)
            
            return mla_text.strip() if mla_text else ""
            
        except Exception as e:
            # 팝업이 열려있다면 닫기 시도
            try:
                await page.keyboard.press('Escape')
            except:
                pass
            return ""
    
    async def run_batch(self, queries: list[str], start_index: int) -> list[tuple[str, list[dict]]]:
        """배치 단위로 검색 실행 (탭 기반 병렬 처리)"""
        batch_results = []
        
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = context.pages[0] if context.pages else await context.new_page()
            
            print(f"\n🌐 브라우저 세션 시작 (병렬 모드)")
            print(f"   프로필: {self.user_data_dir}")
            
            await page.goto(self.SCHOLAR_LABS_URL, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)
            
            # 로그인 체크
            if await self._check_login_required(page):
                print("\n⚠️  Google 로그인 필요!")
                print("    로그인 후 Enter를 누르세요...")
                input()
                await page.goto(self.SCHOLAR_LABS_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(3)
            
            # 일일 한도 체크
            if await self._check_daily_limit(page):
                print("\n❌ 일일 한도 도달!")
                await context.close()
                return batch_results
            
            # 병렬 처리 루프
            prev_tab = None
            prev_query = None
            extraction_task = None
            
            for i, query in enumerate(queries):
                q_num = start_index + i + 1
                print(f"\n[Q{q_num}] {query[:60]}{'...' if len(query) > 60 else ''}")
                
                # 이전 탭의 인용 추출이 진행 중이면 대기
                if extraction_task:
                    print(f"    ⏳ 이전 질문 인용 추출 대기 중...")
                    prev_results = await extraction_task
                    batch_results.append((prev_query, prev_results))
                    print(f"    ✅ 이전 질문: {len(prev_results)}개 완료")
                    await prev_tab.close()
                    extraction_task = None
                
                # 새 탭에서 검색 제출
                current_tab = await context.new_page()
                await current_tab.goto(self.SCHOLAR_LABS_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # 10개 결과 표시 확인까지만 대기
                success = await self.search_scholar_labs_fast(current_tab, query)
                
                if success and i < len(queries) - 1:
                    # 다음 질문이 있으면, 현재 탭의 인용 추출을 백그라운드로 예약
                    print(f"    🔄 다음 질문 진행 (현재 탭 인용은 백그라운드 처리)")
                    extraction_task = asyncio.create_task(
                        self.extract_citations_from_page(current_tab, max_results=10)
                    )
                    prev_tab = current_tab
                    prev_query = query
                else:
                    # 마지막 질문이거나 실패한 경우: 즉시 추출
                    print(f"    📥 인용 정보 추출 중...")
                    results = await self.extract_citations_from_page(current_tab, max_results=10)
                    batch_results.append((query, results))
                    print(f"    ✅ {len(results)}개 완료")
                    await current_tab.close()
                
                # 세션 한도 체크
                if await self._check_session_limit(page):
                    print("\n⚠️  세션 한도 도달")
                    if extraction_task:
                        prev_results = await extraction_task
                        batch_results.append((prev_query, prev_results))
                        await prev_tab.close()
                    break
            
            # 남은 추출 작업 완료
            if extraction_task:
                print(f"\n⏳ 마지막 질문 인용 추출 완료 대기...")
                prev_results = await extraction_task
                batch_results.append((prev_query, prev_results))
                await prev_tab.close()
            
            await context.close()
            print(f"\n🔒 세션 종료 (총 {len(batch_results)}개 완료)")
        
        return batch_results
    
    async def _check_login_required(self, page) -> bool:
        """로그인이 필요한지 확인합니다."""
        try:
            # Google 로그인 페이지 확인
            if 'accounts.google.com' in page.url:
                return True
            # 로그인 버튼 확인
            login_btn = await page.query_selector('a[href*="accounts.google.com"]')
            return login_btn is not None
        except:
            return False
    
    async def _check_daily_limit(self, page) -> bool:
        """일일 한도 도달 여부를 확인합니다."""
        try:
            page_text = await page.inner_text('body')
            limit_keywords = ['일일 한도', 'daily limit', '한도에 도달', 'limit reached']
            return any(kw in page_text.lower() for kw in limit_keywords)
        except:
            return False
    
    async def _check_session_limit(self, page) -> bool:
        """세션 한도 도달 여부를 확인합니다."""
        try:
            page_text = await page.inner_text('body')
            session_keywords = ['세션 한도', 'session limit', '세션이 만료']
            return any(kw in page_text.lower() for kw in session_keywords)
        except:
            return False
    
    def format_results_markdown(self, all_query_results: list[tuple[str, list[dict]]], 
                                 start_q_num: int = 1, 
                                 append_mode: bool = False) -> str:
        """검색 결과를 Markdown 형식으로 포맷합니다."""
        lines = []
        
        if not append_mode:
            lines = [
                "# Google Scholar Labs 시맨틱 검색 결과",
                "",
                f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "",
                "---",
                ""
            ]
        
        for i, (query, results) in enumerate(all_query_results):
            q_num = start_q_num + i
            lines.append(f"### Q{q_num}: {query}")
            lines.append("")
            
            if not results:
                lines.append("*검색 결과가 없습니다.*")
                lines.append("")
                continue
            
            for j, r in enumerate(results, 1):
                # 1. 번호와 제목 (링크 포함)
                title = r.get('title', 'Untitled')
                link = r.get('link', '')
                
                if link:
                    lines.append(f"**{j}. [{title}]({link})**")
                else:
                    lines.append(f"**{j}. {title}**")
                lines.append("")
                
                # 2. 메타 정보 (저자 - 저널, 연도 - 출판사)
                if r.get('meta'):
                    lines.append(f"{r['meta']}")
                    lines.append("")
                
                # 3. 주요 설명 (첫 번째 스니펫 문장)
                if r.get('snippet'):
                    snippet = r['snippet'].replace('\n', ' ').strip()
                    # 첫 문장은 일반 텍스트로
                    sentences = re.split(r'(?<=[.!?])\s+', snippet)
                    if sentences:
                        lines.append(sentences[0])
                        lines.append("")
                        # 나머지 문장들은 bullet point로
                        for sent in sentences[1:]:
                            if sent.strip():
                                lines.append(f"• {sent.strip()}")
                        if len(sentences) > 1:
                            lines.append("")
                
                # 4. 인용 수
                if r.get('citations'):
                    lines.append(f"📚 {r['citations']}")
                    lines.append("")
                
                # 5. MLA 인용 형식 (파이프라인 호환: MLA만 출력)
                if r.get('mla_citation'):
                    lines.append(f"> {r['mla_citation']}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_citation(self, result: dict) -> str:
        """학술 인용 형식을 생성합니다."""
        meta = result.get('meta', '')
        title = result.get('title', '')
        
        if not meta:
            return ""
        
        # 메타 정보 파싱: "저자 - 저널, 연도 - 출판사" 형식
        # 예: "TD Stegman - Theological studies, 2011 - journals.sagepub.com"
        
        parts = meta.split(' - ')
        
        if len(parts) >= 2:
            authors_raw = parts[0].strip()
            
            # 저자 이름 정리 (이니셜 + 성 -> 성, 이니셜)
            author_parts = authors_raw.split(', ')
            authors = []
            for author in author_parts[:3]:  # 최대 3명
                author = author.strip()
                if author:
                    # "TD Stegman" -> "Stegman, T. D." 형식으로 변환 시도
                    words = author.split()
                    if len(words) >= 2:
                        initials = words[:-1]
                        surname = words[-1]
                        formatted_initials = '. '.join(list(''.join(initials))) + '.'
                        authors.append(f"{surname}, {formatted_initials}")
                    else:
                        authors.append(author)
            
            author_str = ', '.join(authors)
            if len(author_parts) > 3:
                author_str += ", et al."
            
            # 저널과 연도 추출
            journal_year = parts[1] if len(parts) > 1 else ""
            year_match = re.search(r'(\d{4})', journal_year)
            year = year_match.group(1) if year_match else ""
            journal = re.sub(r',?\s*\d{4}', '', journal_year).strip()
            
            # 인용 형식 조합
            if author_str and title and journal and year:
                return f'{author_str} "{title}." {journal} ({year}).'
            elif author_str and title and year:
                return f'{author_str} "{title}." ({year}).'
        
        return ""
    
    def _clean_citations_mla_only(self, markdown: str) -> str:
        """APA, ISO 690 인용을 제거하고 MLA 인용만 남깁니다."""
        lines = markdown.split('\n')
        cleaned_lines = []
        skip_next_empty = False
        
        for i, line in enumerate(lines):
            # APA 형식 감지: 저자 (연도). 제목.
            # ISO 690 형식 감지: 저자. 제목. 저널, 연도, 권(호): 페이지
            if line.startswith('>'):
                content = line[1:].strip()
                # APA 패턴: "저자, A. B. (2020)." 또는 "(2011)." 포함
                if re.search(r'\(\d{4}\)\.', content):
                    skip_next_empty = True
                    continue
                # ISO 690 패턴: "저자. 제목. 저널, 연도, 권.호: 페이지" (콜론+숫자 패턴)
                elif re.search(r'\d+\.\d+:\s*\d+-\d+', content):
                    skip_next_empty = True
                    continue
            
            # 빈 줄 스킵 처리
            if skip_next_empty and line.strip() == '':
                skip_next_empty = False
                continue
            
            skip_next_empty = False
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def save_results(self, markdown: str, append: bool = False):
        """결과를 파일에 저장 (누적 또는 새로 생성, MLA 인용만 유지)"""
        if append and self.output_file.exists():
            existing = self.output_file.read_text(encoding='utf-8')
            markdown = existing + "\n" + markdown
        
        # MLA 인용만 남기고 APA, ISO 690 제거
        markdown = self._clean_citations_mla_only(markdown)
        
        self.output_file.write_text(markdown, encoding='utf-8')
        return self.output_file
    
    async def run(self, queries_input: str = None, resume: bool = False):
        """에이전트를 실행합니다."""
        print("=" * 60)
        print("Google Scholar Labs 시맨틱 검색 에이전트 v2")
        print(f"  • 배치 크기: {self.BATCH_SIZE}개/세션")
        print(f"  • 세션 제한 대응: 자동 브라우저 재시작")
        print("=" * 60)
        
        # 이전 상태 확인
        state = self.load_state()
        
        if resume and state["completed_queries"]:
            print(f"\n📂 이전 검색 재개: {len(state['completed_queries'])}개 완료됨")
        else:
            state = {"completed_queries": [], "results": []}
        
        # 질문 입력 받기
        if queries_input is None:
            print("\n검색 질문을 입력하세요 (빈 줄 2번으로 입력 완료):")
            print("-" * 40)
            lines = []
            empty_count = 0
            
            while True:
                try:
                    line = input()
                    if line == "":
                        empty_count += 1
                        if empty_count >= 2:
                            break
                    else:
                        empty_count = 0
                    lines.append(line)
                except EOFError:
                    break
            
            queries_input = '\n'.join(lines)
        
        # 질문 파싱
        all_queries = self.parse_queries(queries_input)
        
        if not all_queries:
            print("유효한 검색 질문이 없습니다.")
            return
        
        # 이미 완료된 질문 제외
        remaining_queries = [q for q in all_queries if q not in state["completed_queries"]]
        
        print(f"\n📋 총 질문: {len(all_queries)}개")
        print(f"   완료됨: {len(state['completed_queries'])}개")
        print(f"   남은 질문: {len(remaining_queries)}개")
        
        if not remaining_queries:
            print("\n모든 질문이 이미 완료되었습니다.")
            return
        
        # 배치로 나누기
        batches = [remaining_queries[i:i + self.BATCH_SIZE] 
                   for i in range(0, len(remaining_queries), self.BATCH_SIZE)]
        
        print(f"   배치 수: {len(batches)}개 ({self.BATCH_SIZE}개/배치)")
        
        # 각 배치 실행
        all_batch_results = []
        processed_count = len(state["completed_queries"])
        
        for batch_idx, batch in enumerate(batches):
            print(f"\n{'='*40}")
            print(f"📦 배치 {batch_idx + 1}/{len(batches)} 실행 중...")
            print(f"{'='*40}")
            
            batch_results = await self.run_batch(batch, processed_count)
            all_batch_results.extend(batch_results)
            
            # 상태 업데이트 및 저장
            for query, results in batch_results:
                state["completed_queries"].append(query)
                state["results"].append({"query": query, "results": results})
            
            self.save_state(state)
            
            # 결과 누적 저장
            is_first_batch = (batch_idx == 0 and processed_count == 0)
            markdown = self.format_results_markdown(
                batch_results, 
                start_q_num=processed_count + 1,
                append_mode=not is_first_batch
            )
            output_file = self.save_results(markdown, append=not is_first_batch)
            
            processed_count += len(batch)
            
            print(f"\n💾 중간 저장 완료: {output_file}")
            
            # 다음 배치 전 대기 (세션 쿨다운)
            if batch_idx < len(batches) - 1:
                cooldown = 10
                print(f"\n⏳ 세션 쿨다운 대기 중... ({cooldown}초)")
                await asyncio.sleep(cooldown)
        
        # 완료
        self.clear_state()  # 상태 파일 정리
        
        print()
        print("=" * 60)
        print(f"✅ 완료! 총 {len(all_queries)}개 질문 검색됨")
        print(f"📄 결과 파일: {output_file}")
        print("=" * 60)


async def main():
    # 명령줄 인자 처리
    profile = "default"
    job = None  # None이면 타임스탬프로 자동 생성
    resume = "--resume" in sys.argv
    
    # --profile 옵션 처리
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--profile" and i < len(sys.argv) - 1:
            profile = sys.argv[i + 1]
        elif arg.startswith("--profile="):
            profile = arg.split("=")[1]
    
    # --job 옵션 처리
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--job" and i < len(sys.argv) - 1:
            job = sys.argv[i + 1]
        elif arg.startswith("--job="):
            job = arg.split("=")[1]
    
    # --list-profiles: 등록된 프로필 목록 보기
    if "--list-profiles" in sys.argv:
        profiles_dir = Path(__file__).parent / ".profiles"
        if profiles_dir.exists():
            profiles = [p.name for p in profiles_dir.iterdir() if p.is_dir()]
            print("📁 등록된 프로필:")
            for p in profiles:
                print(f"   • {p}")
        else:
            print("등록된 프로필이 없습니다.")
        return
    
    # --list-jobs: 진행 중인 작업 목록 보기
    if "--list-jobs" in sys.argv:
        results_dir = Path(__file__).parent / "results"
        if results_dir.exists():
            states = list(results_dir.glob(".state_*.json"))
            if states:
                print("📋 진행 중인 작업:")
                for s in states:
                    job_name = s.stem.replace(".state_", "")
                    print(f"   • {job_name}")
            else:
                print("진행 중인 작업이 없습니다.")
        return
    
    agent = ScholarLabsAgent(profile=profile, job=job)
    
    # 파일에서 질문 읽기
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            continue
        queries_file = Path(arg)
        if queries_file.exists():
            queries_input = queries_file.read_text(encoding='utf-8')
            await agent.run(queries_input, resume=resume)
            return
    
    # 대화형 모드
    await agent.run(resume=resume)


if __name__ == "__main__":
    asyncio.run(main())


