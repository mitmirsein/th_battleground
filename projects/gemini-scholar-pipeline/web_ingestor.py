#!/usr/bin/env python3
"""
Web Ingestor for Gemini Scholar Pipeline
- Parses 'Deep Research' raw reports to find 'Referenced Sources'.
- Fetches content from URLs (HTML/PDF) using Playwright.
- Ingests into 'scholar_kb.db' via kb_manager.py.
"""

import sys
import re
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime
from kb_manager import ScholarKnowledgeBase

class WebIngestor:
    def __init__(self):
        self.kb = ScholarKnowledgeBase()
        self.kb.init_db()  # Ensure DB exists/updated

    async def ingest_report(self, report_path: str):
        path = Path(report_path)
        if not path.exists():
            print(f"❌ File not found: {path}")
            return

        print(f"📂 Parsing Report: {path.name}")
        content = path.read_text(encoding='utf-8')
        
        # Extract References
        # Pattern: [Title], [Date Access], [URL]
        # Or simple lines with http at the end
        # We look for the "참고 자료" or "References" section at the end.
        
        # 1. Find Reference Section
        ref_start_keywords = ["참고 자료", "References", "Sources"]
        start_index = -1
        for kw in ref_start_keywords:
            idx = content.rfind(kw)
            if idx != -1:
                start_index = idx
                break
        
        if start_index == -1:
            print("⚠️ No reference section found.")
            return

        ref_section = content[start_index:]
        lines = ref_section.split('\n')
        
        urls_to_ingest = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Simple URL extraction
            url_match = re.search(r'https?://[^\s,]+', line)
            if url_match:
                url = url_match.group(0)
                # Cleanup trailing punctuation
                url = url.rstrip('.,)]"')
                
                # Title extraction (everything before URL)
                title = line.replace(url, '').strip(' ,-')
                
                # Cleanup "Date Accessed" if present
                title = re.sub(r'\d{1,2}월 \d{1,2}, \d{4}에 액세스', '', title).strip(' ,-')
                
                urls_to_ingest.append({
                    "url": url,
                    "title": title or "Untitled Web Source",
                    "original_line": line
                })

        print(f"🔍 Found {len(urls_to_ingest)} URLs.")
        
        # 2. Fetch & Ingest
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set User Agent to avoid blocking
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            # Process URLs
            from tqdm import tqdm
            count = 0
            for item in tqdm(urls_to_ingest, desc="Ingesting Web Refs"):
                success = await self._process_url(page, item, path.stem)
                if success:
                    count += 1
            
            await browser.close()
            print(f"✅ Ingestion Complete: {count}/{len(urls_to_ingest)} saved.")

    async def _process_url(self, page, item, topic):
        url = item['url']
        print(f"   🌐 Fetching: {url[:60]}...")
        
        try:
            # Handle PDF
            if url.lower().endswith('.pdf'):
                print("      ⚠️ PDF parsing not fully supported (saving URL entry).")
                # For now, we save metadata only for PDFs unless we add pypdf
                # Simple fetch to check existence
                # await page.goto(url, wait_until="commit")
                # content_text = "[PDF Document] Content extraction requires PDF tool."
                content_text = f"PDF Document: {item['title']}"
            else:
                # HTML
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    # Extract main text (simple body text)
                    content_text = await page.evaluate("document.body.innerText")
                    # Cleanup excessive newlines
                    content_text = re.sub(r'\n{3,}', '\n\n', content_text)
                except Exception as e:
                    print(f"      ❌ Timeout or Error: {e}")
                    return False

            # Create Entry
            entry = {
                "title": item['title'],
                "url": url,
                "snippet": content_text[:300].strip(), # Abstract/Snippet
                "raw_markdown": content_text, # Full content
                "source_type": "web_reference",
                "query": topic, # Use topic as query source
                "year": datetime.now().year # Default to current year if unknown
            }
            
            # Ingest
            if self.kb.insert_paper(entry):
                print("      ✅ Saved to DB")
                return True
            else:
                print("      ⚠️ Duplicate (skipped)")
                return False

        except Exception as e:
            print(f"      ❌ Unexpected Error: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python web_ingestor.py <report_path>")
        sys.exit(1)
        
    ingestor = WebIngestor()
    asyncio.run(ingestor.ingest_report(sys.argv[1]))
