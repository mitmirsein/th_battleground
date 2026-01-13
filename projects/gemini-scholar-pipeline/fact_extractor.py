#!/usr/bin/env python3
"""
Fact Extractor (Phase 3)
- SQLite DB에서 처리되지 않은 논문(fact_extracted=0)을 로드
- 배치 단위로 Gemini에게 프롬프트 전송 (Claims, Evidence, Stats, Quotes 추출)
- 결과를 파싱하여 `facts` 테이블에 저장
"""

import asyncio
import json
import sqlite3
import re
from pathlib import Path
from typing import List, Dict

from playwright.async_api import async_playwright
from kb_manager import ScholarKnowledgeBase

class FactExtractor:
    GEMINI_URL = "https://gemini.google.com"
    BATCH_SIZE = 2
    PROMPT_FILE = Path(__file__).parent / "prompts/fact_extraction_prompt.md"
    
    def __init__(self, db_path: str = None):
        self.kb = ScholarKnowledgeBase(db_path)
        
    def load_prompt(self) -> str:
        if self.PROMPT_FILE.exists():
            return self.PROMPT_FILE.read_text(encoding='utf-8')
        print(f"❌ Prompt file not found: {self.PROMPT_FILE}")
        return ""

    def get_pending_papers(self, limit: int = 20) -> List[Dict]:
        """처리 대기 중인 논문 가져오기"""
        conn = self.kb.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, abstract, raw_markdown 
            FROM papers 
            WHERE fact_extracted = 0 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        papers = []
        for row in rows:
            # abstract가 비어있으면 raw_markdown에서 일부 추출 시도 (간단히)
            snippet = row['abstract']
            if not snippet or len(snippet) < 10:
                snippet = row['raw_markdown'][:500].replace('\n', ' ')
            
            papers.append({
                'id': row['id'],
                'title': row['title'],
                'snippet': snippet
            })
            
        conn.close()
        return papers

    def save_facts(self, facts: List[Dict]):
        """추출된 Fact 저장"""
        conn = self.kb.get_connection()
        cursor = conn.cursor()
        
        count = 0
        paper_ids = set()
        
        for fact in facts:
            try:
                cursor.execute("""
                    INSERT INTO facts (id, paper_id, fact_type, content, context, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (
                    str(uuid.uuid4()),
                    fact['paper_id'],
                    fact['type'],
                    fact['content'],
                    fact.get('context', ''),
                ))
                count += 1
                paper_ids.add(fact['paper_id'])
            except Exception as e:
                print(f"⚠️ Insert Error: {e}")
        
        # Mark papers as processed
        for pid in paper_ids:
            cursor.execute("UPDATE papers SET fact_extracted = 1 WHERE id = ?", (pid,))
            
        conn.commit()
        conn.close()
        print(f"✅ Saved {count} facts from {len(paper_ids)} papers.")

    async def run(self):
        print(f"🚀 Starting Fact Extraction (Phase 3)...")
        
        papers = self.get_pending_papers()
        if not papers:
            print("🎉 No pending papers to process.")
            return
            
        print(f"📋 Found {len(papers)} pending papers.")
        base_prompt = self.load_prompt()
        if not base_prompt: return
        
        # Batches
        batches = [papers[i:i + self.BATCH_SIZE] for i in range(0, len(papers), self.BATCH_SIZE)]
        
        async with async_playwright() as p:
            # Browser Setup (Reuse logic mostly)
            user_data_dir = Path(__file__).parent / ".profiles/account1"
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = context.pages[0] if context.pages else await context.new_page()
            
            await page.goto(self.GEMINI_URL, wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # 3. Process Batches
            total_extracted = 0
            
            for i, batch in enumerate(tqdm(batches, desc="Extracting Facts"), 1):
                # print(f"\n📦 Processing Batch {i}/{len(batches)} ({len(batch)} items)...") # tqdm covers this
                
                # Construct Payload
                payload = ""
                for paper in batch:
                    payload += f"- **ID:** {paper['id']}\n"
                    payload += f"- **Snippet:** {paper['snippet']}\n\n"
                    
                full_prompt = base_prompt.replace("[Paper Snippets]", payload) 
                
                # Append Marker
                MARKER = "---GEMINI_EXTRACT_START---"
                final_message = full_prompt + "\n\n# Input:\n" + payload + \
                                f"\n\n{MARKER}\nIMPORTANT: Output ONLY standard JSON format found in the template."
                
                # Send to Gemini
                await self._interact_with_gemini(page, final_message)
                
                # Get Response (Select All Strategy)
                response_text = await self._get_last_response_select_all(page, MARKER)
                
                # Parse JSON
                facts = self._extract_json(response_text)
                
                if facts:
                    self.save_facts(facts)
                else:
                    print("⚠️ No valid JSON found in response.")
                    # Debug: print last 200 chars to see what we got
                    print(f"🛑 Raw Response Snippet: ...{response_text[-300:]}")
                    
                await asyncio.sleep(2) # Cool down
            
            await context.close()

    async def _interact_with_gemini(self, page, message: str):
        """Send message to Gemini (Robust Version)"""
        try:
            # 1. Input Box Finding (Robust)
            input_found = False
            input_selectors = [
                'div[contenteditable="true"]',
                'textarea',
                '.ql-editor',
                '[aria-label*="메시지"]',
                '[aria-label*="Message"]',
            ]
            
            for selector in input_selectors:
                try:
                    input_el = await page.query_selector(selector)
                    if input_el:
                        await input_el.click()
                        await asyncio.sleep(0.5)
                        
                        # Safe text entry (Chunked)
                        chunk_size = 1000
                        for i in range(0, len(message), chunk_size):
                            chunk = message[i:i+chunk_size]
                            await page.evaluate(f'document.execCommand("insertText", false, {json.dumps(chunk)})')
                            await asyncio.sleep(0.1)
                            
                        await asyncio.sleep(1)
                        print("   ✓ Prompt entered.")
                        input_found = True
                        break
                except Exception as e:
                    continue
            
            if not input_found:
                raise Exception("Input box not found")
                
            # 2. Send Button (Robust)
            sent = False
            send_selectors = [
                'button[aria-label*="보내"]',
                'button[aria-label*="Send"]',
                'button[aria-label*="submit"]',
                'button.send-button',
                '[data-test-id="send-button"]',
            ]
            
            for selector in send_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        sent = True
                        print("   ✓ Send button clicked.")
                        break
                except:
                    continue
                    
            if not sent:
                await page.keyboard.press("Enter")
                print("   ✓ Check Enter key sent.")
                
            print("   📤 Sent prompt to Gemini...")
            
            # 3. Wait for Response (Robust)
            await asyncio.sleep(8) # Initial wait
            
            # Wait for generation indicator (stop button disappearing or copy button appearing)
            # Just wait a safe amount of time for short responses, or verify content length changes?
            # Simple heuristic: wait for the stop button to be GONE.
            try:
                # 'stop-button' might be visible during generation. 
                # Better: wait for a "Copy" button to appear (even if we don't click it, it signifies completion)
                await page.wait_for_selector('copy-code-button, button[aria-label*="Copy"]', timeout=60000)
                print("   ✓ Response generation likely complete.")
            except:
                print("   ⚠️ specific completion indicator not found. Proceeding...")
            
        except Exception as e:
            print(f"   ❌ Interaction Error: {e}")

    async def _get_last_response_select_all(self, page, marker: str) -> str:
        """Get response using Select All + Copy + Parse Marker"""
        try:
            # Focus page
            await page.click('body')
            await asyncio.sleep(0.5)
            
            # Select All
            await page.keyboard.press('Meta+a')
            await asyncio.sleep(0.5)
            
            # Copy
            await page.keyboard.press('Meta+c')
            await asyncio.sleep(1)
            
            # Read Clipboard
            import subprocess
            full_text = subprocess.check_output(['pbpaste']).decode('utf-8')
            
            # Parse
            if marker in full_text:
                parts = full_text.split(marker)
                last_part = parts[-1] 
                # The marker is in the USER message. The text AFTER it includes:
                # 1. The rest of the user message (if any)
                # 2. The Model response.
                
                # Usually Gemini formats user message distinct from model.
                # But 'full_text' is raw text.
                # "IMPORTANT: Output ONLY..." (end of prompt) -> Model Response.
                
                # Let's assume the text immediately following the marker + a bit of prompt is the response.
                # Or just return 'last_part' and let _extract_json find the JSON list within it.
                return last_part
            else:
                print("   ⚠️ Marker not found in clipboard text.")
                return full_text # Fallback
                
        except Exception as e:
            print(f"   ❌ Clipboard Error: {e}")
        return ""

    def _extract_json(self, text: str) -> List[Dict]:
        """Extract JSON list from markdown text"""
        try:
            # Find JSON block ```json ... ```
            match = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Or just find [...]
            match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
        return []

if __name__ == "__main__":
    import uuid
    extractor = FactExtractor()
    asyncio.run(extractor.run())
