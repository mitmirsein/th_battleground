import asyncio
import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright
import sys

# 프로젝트 루트를 경로에 추가 (utils 접근을 위해)
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.local_pdf_processor import process_pdf, tiktoken_len
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    print("⚠️ PDF processing utilities not available")


class AgentBrowser:
    """Agent-Browser CLI wrapper for AI-friendly web automation"""
    
    def __init__(self, session: str = "librarian"):
        self.session = session
        
    def _run(self, cmd: List[str], json_output: bool = False) -> Dict:
        """Execute agent-browser command"""
        full_cmd = ["agent-browser"] + cmd
        if json_output:
            full_cmd.append("--json")
        full_cmd.extend(["--session", self.session])
        
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        if json_output:
            try:
                return json.loads(result.stdout)
            except:
                return {"success": False, "raw": result.stdout}
        
        return {"success": True, "stdout": result.stdout}
    
    def open(self, url: str): return self._run(["open", url])
    def wait(self, ms: int): return self._run(["wait", str(ms)])
    def snapshot(self): return self._run(["snapshot", "-i"], json_output=True)
    def get_text(self, ref: str): return self._run(["get", "text", ref], json_output=True)
    def click(self, ref: str): return self._run(["click", ref])
    def screenshot(self, path: str): return self._run(["screenshot", path])
    def close(self): return self._run(["close"])


class LibrarianAgent:
    """
    정보수집관 (Librarian)
    - 외부 웹 URL 콘텐츠 추출
    - 로컬 PDF 파일 정제 및 텍스트화
    - agent-browser를 통한 AI 친화적 스크래핑
    """
    
    def __init__(self, persona_path: Optional[str] = None):
        self.persona_path = persona_path
        self.name = "Librarian"
        self.browser = AgentBrowser("librarian_session")
        
    async def collect_web(self, url: str) -> Dict[str, Any]:
        """웹 URL에서 본문 텍스트 추출 (기존 Playwright 방식)"""
        print(f"🌐 [{self.name}] 웹 수집 시작: {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle")
                title = await page.title()
                content = await page.evaluate("document.body.innerText")
                
                print(f"✅ [{self.name}] 수집 완료: {title}")
                return {
                    "source": url,
                    "title": title,
                    "content": content,
                    "type": "web"
                }
            except Exception as e:
                print(f"❌ [{self.name}] 웹 수집 오류: {e}")
                return {"error": str(e)}
            finally:
                await browser.close()

    def collect_web_agent(self, url: str, wait_ms: int = 5000) -> Dict[str, Any]:
        """
        agent-browser를 사용한 웹 수집 (동기식, AI 친화적)
        Returns: snapshot with refs for further interaction
        """
        print(f"🤖 [{self.name}] Agent-Browser 수집 시작: {url}")
        
        self.browser.open(url)
        self.browser.wait(wait_ms)
        
        snapshot = self.browser.snapshot()
        
        if snapshot.get("success"):
            refs = snapshot.get("data", {}).get("refs", {})
            print(f"✅ [{self.name}] 발견된 요소: {len(refs)}개")
            return {
                "source": url,
                "snapshot": snapshot.get("data", {}).get("snapshot", ""),
                "refs": refs,
                "type": "agent-browser"
            }
        else:
            print(f"❌ [{self.name}] 스냅샷 실패: {snapshot.get('error')}")
            return {"error": snapshot.get("error", "Unknown error")}

    def scrape_journal_toc(self, journal: str, band: int, heft: int) -> List[Dict]:
        """
        저널 목차 스크래핑 (저널별 로직)
        
        Args:
            journal: 저널 약칭 (kud, evth, znw)
            band: 권 번호
            heft: 호 번호
        
        Returns:
            List of article dicts: [{title, author, pages}, ...]
        """
        urls = {
            "kud": f"https://www.vr-elibrary.de/toc/kud/{band}/{heft}",
            "evth": f"https://www.degruyter.com/journal/key/evth/volume/{band}/issue/{heft}/html",
            "znw": f"https://www.degruyter.com/journal/key/znw/volume/{band}/issue/{heft}/html"
        }
        
        url = urls.get(journal.lower())
        if not url:
            return [{"error": f"지원하지 않는 저널: {journal}"}]
        
        print(f"📚 [{self.name}] 저널 스크래핑: {journal.upper()} {band}/{heft}")
        
        result = self.collect_web_agent(url, wait_ms=8000)
        
        if "error" in result:
            return [result]
        
        # Extract articles from snapshot (저널별 파싱 로직 필요)
        articles = self._parse_journal_snapshot(result, journal)
        
        print(f"✅ [{self.name}] 발견된 논문: {len(articles)}편")
        return articles
    
    def _parse_journal_snapshot(self, result: Dict, journal: str) -> List[Dict]:
        """스냅샷에서 논문 정보 추출 (저널별 로직)"""
        refs = result.get("refs", {})
        articles = []
        
        for ref_id, elem in refs.items():
            role = elem.get("role", "")
            name = elem.get("name", "")
            
            # 논문 제목 패턴 (heading level 3 or link with article pattern)
            if role in ["heading", "link"] and len(name) > 20:
                # 간단한 휴리스틱: 20자 이상의 heading/link는 논문 제목일 가능성
                articles.append({
                    "title": name,
                    "ref": ref_id,
                    "journal": journal.upper()
                })
        
        return articles

    def close_browser(self):
        """브라우저 세션 종료"""
        self.browser.close()

    def collect_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """로컬 PDF 가공 (utils.local_pdf_processor 활용)"""
        print(f"📄 [{self.name}] PDF 가공 시작: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            return {"error": f"파일을 찾을 수 없습니다: {pdf_path}"}
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=560,
            separators=["\n\n\n", "\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""],
            length_function=tiktoken_len,
        )
        
        try:
            chunks = process_pdf(pdf_path, text_splitter)
            full_text = "\n\n".join([c['text'] for c in chunks])
            
            print(f"✅ [{self.name}] PDF 가공 완료: {len(chunks)}개 청크 생성")
            return {
                "source": pdf_path,
                "title": Path(pdf_path).name,
                "chunks": chunks,
                "full_text": full_text,
                "type": "pdf"
            }
        except Exception as e:
            print(f"❌ [{self.name}] PDF 가공 오류: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ARC Secretariat - Librarian Agent")
    parser.add_argument("--url", type=str, help="Collect content from a web URL")
    parser.add_argument("--pdf", type=str, help="Process a local PDF file")
    parser.add_argument("--journal", type=str, help="Scrape journal TOC (kud, evth, znw)")
    parser.add_argument("--band", type=int, help="Journal volume number")
    parser.add_argument("--heft", type=int, help="Journal issue number")
    parser.add_argument("--agent", action="store_true", help="Use agent-browser instead of Playwright")
    
    args = parser.parse_args()
    
    async def run_cli():
        lib = LibrarianAgent()
        
        if args.journal and args.band and args.heft:
            # 저널 스크래핑
            result = lib.scrape_journal_toc(args.journal, args.band, args.heft)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            lib.close_browser()
        elif args.url:
            if args.agent:
                result = lib.collect_web_agent(args.url)
                lib.close_browser()
            else:
                result = await lib.collect_web(args.url)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.pdf:
            result = lib.collect_pdf(args.pdf)
            if "chunks" in result:
                del result["chunks"]
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            parser.print_help()
    
    if args.url or args.pdf or (args.journal and args.band and args.heft):
        asyncio.run(run_cli())

