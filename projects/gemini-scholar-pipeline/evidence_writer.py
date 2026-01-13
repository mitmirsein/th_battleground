#!/usr/bin/env python3
"""
Evidence Writer (Phase 4)
- 입력된 Topic에 대해 SQLite에서 Fact 검색 (Keyword Match)
- 검색된 Fact를 프롬프트에 주입
- Gemini에게 글쓰기 요청 (Select-All Copy 전략 사용)
"""

import asyncio
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright
from kb_manager import ScholarKnowledgeBase

class EvidenceWriter:
    GEMINI_URL = "https://gemini.google.com"
    PROMPT_FILE = Path(__file__).parent / "prompts/evidence_writing_prompt.md"
    
    def __init__(self, topic: str):
        self.topic = topic
        self.kb = ScholarKnowledgeBase()
        
    def load_prompt(self) -> str:
        if self.PROMPT_FILE.exists():
            return self.PROMPT_FILE.read_text(encoding='utf-8')
        return ""

    def retrieve_facts(self) -> str:
        """Topic 관련 Fact 검색 (Simple Keyword Match)"""
        conn = self.kb.get_connection()
        cursor = conn.cursor()
        
        # 키워드 분리 (예: "Moltmann Zimzum" -> ["Moltmann", "Zimzum"])
        keywords = self.topic.split()
        if not keywords: return ""
        
        query = "SELECT paper_id, fact_type, content, context FROM facts WHERE "
        conditions = []
        params = []
        
        for kw in keywords:
            conditions.append("(content LIKE ? OR context LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%"])
            
        query += " AND ".join(conditions)
        query += " LIMIT 20" # 너무 많으면 프롬프트 초과 우려
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        fact_text = ""
        for row in rows:
            pid, ftype, content, ctx = row
            # 저자 정보 가져오기 (Optional join, here just separate query for simplicity or ignore)
            # 여기서는 Fact 자체에 집중
            fact_text += f"- [{pid[:8]}] ({ftype}) {content} (Context: {ctx})\n"
            
        conn.close()
        return fact_text

    async def auto_research(self):
        """Execute Recursive Research Loop"""
        print(f"🔄 Auto-Research Triggered for: '{self.topic}'")
        
        # 1. Search (Scholar Labs Agent)
        print("   🔎 Running Scholar Search...")
        try:
            cmd = [
                sys.executable, "scholar_labs_agent.py",
                "--topic", self.topic,
                "--pages", "1",
                "--profile", "account1" 
            ]
            subprocess.run(cmd, check=True)
            print("   ✅ Search complete.")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Search failed: {e}")
            return

        # 2. Ingest (KB Manager)
        print("   📥 Ingesting Results...")
        results_dir = Path("results")
        # Ingest recent files or all (simple: all)
        for f in results_dir.glob("*.md"):
             self.kb.ingest_markdown_file(f)
             
        # 3. Extract Facts (Fact Extractor)
        print("   ⛏️  Extracting Facts...")
        from fact_extractor import FactExtractor
        extractor = FactExtractor()
        # We need to run the async extractor. 
        # Since we are already in an async loop, we can't easily run another async loop if not careful.
        # But FactExtractor.run is async.
        await extractor.run()
        print("   ✅ Fact Extraction complete.")

    async def run(self):
        print(f"🚀 Starting Evidence Writer for Topic: '{self.topic}'")
        
        # 1. Retrieve Facts (Initial)
        facts_payload = self.retrieve_facts()
        fact_count = facts_payload.count("- [")
        
        # RECURSIVE CHECK
        if fact_count < 3:
            print(f"⚠️ Insufficient facts found ({fact_count}). Initiating Auto-Research...")
            await self.auto_research()
            
            # Retry Retrieval
            facts_payload = self.retrieve_facts()
            fact_count = facts_payload.count("- [")
            print(f"📚 Retrieved Facts after Research: {fact_count}")
        
        if not facts_payload:
            print("⚠️ Still no relevant facts found. Proceeding with best effort (or skipping).")
            # return # Optional: Skip generation if strictly empty
            
        print(f"📚 Retrieved Facts Snippet:\n{facts_payload[:200]}...")
        
        # 2. Prepare Prompt
        base_prompt = self.load_prompt()
        final_message = base_prompt.replace("[Topic]", self.topic).replace("[Facts]", facts_payload)
        
        # Marker for Extraction
        MARKER = "---GEMINI_WRITE_START---"
        final_message += f"\n\n{MARKER}\nIMPORTANT: Write the section below this line."
        
        # 3. Generate with Gemini
        async with async_playwright() as p:
            user_data_dir = Path(__file__).parent / ".profiles/account1"
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = context.pages[0] if context.pages else await context.new_page()
            
            await page.goto(self.GEMINI_URL, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Force New Chat
            print("   🔄 Starting New Chat...")
            try:
                new_chat_selectors = ['button[aria-label*="새"]', 'button[aria-label*="New"]', 'a[href="/app"]', '[data-test-id="new-chat"]', '.new-chat-button']
                for sel in new_chat_selectors:
                    btn = await page.query_selector(sel)
                    if btn:
                        await btn.click()
                        await asyncio.sleep(2)
                        break
            except Exception as e:
                print(f"   ⚠️ Could not click new chat: {e}")
            
            await self._interact_with_gemini(page, final_message)
            
            # Select All Strategy
            result = await self._get_last_response_select_all(page, MARKER)
            
            print("\n📝 Generated Draft:\n")
            print(result)
            
            # Save Draft
            draft_file = Path("draft_section.md")
            draft_file.write_text(result, encoding='utf-8')
            print(f"\n💾 Saved to {draft_file}")
            
            await context.close()

    async def _interact_with_gemini(self, page, message: str):
        """Send message (Reused from FactExtractor)"""
        try:
            # Input Finding
            input_found = False
            input_selectors = ['div[contenteditable="true"]', 'textarea', '.ql-editor', '[aria-label*="메시지"]']
            
            for selector in input_selectors:
                try:
                    input_el = await page.query_selector(selector)
                    if input_el:
                        await input_el.click()
                        await asyncio.sleep(0.5)
                        
                        # Chunked Entry
                        chunk_size = 1000
                        for i in range(0, len(message), chunk_size):
                            chunk = message[i:i+chunk_size]
                            await page.evaluate(f'document.execCommand("insertText", false, {json.dumps(chunk)})')
                            await asyncio.sleep(0.1)
                        
                        await asyncio.sleep(1)
                        input_found = True
                        break
                except: continue
                
            if not input_found: raise Exception("Input box not found")
            
            # Send
            await page.keyboard.press("Enter")
            print("   📤 Prompt sent.")
            
            # Wait
            await asyncio.sleep(10)
            try:
                await page.wait_for_selector('copy-code-button, button[aria-label*="Copy"]', timeout=60000)
            except:
                print("   ⚠️ Generation indicator timeout")
                
        except Exception as e:
            print(f"   ❌ Interaction Error: {e}")

    async def _get_last_response_select_all(self, page, marker: str) -> str:
        """Select All + Copy"""
        try:
            await page.click('body')
            await asyncio.sleep(0.5)
            await page.keyboard.press('Meta+a')
            await asyncio.sleep(0.5)
            await page.keyboard.press('Meta+c')
            await asyncio.sleep(1)
            
            full_text = subprocess.check_output(['pbpaste']).decode('utf-8')
            
            if marker in full_text:
                return full_text.split(marker)[-1].strip()
            return full_text
        except Exception as e:
            print(f"   ❌ Clipboard Error: {e}")
            return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evidence_writer.py 'Topic String'")
        sys.exit(1)
    
    topic = sys.argv[1]
    writer = EvidenceWriter(topic)
    asyncio.run(writer.run())
