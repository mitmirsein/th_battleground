"""
Bible Analyze 6.0 Pro - Browser Automation Tool (Playwright)
Author: Gemini Agent
Date: 2025-12-07

Description:
    Semi-automated Browser Agent for Bible Analysis.
    Launches Chrome, waits for user login, then automates the prompt insertion.
    
Usage:
    python analyze_browser.py "요한복음 1:1"
"""

import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

PROMPT_DIR = Path("성경구절분석 6.0")

STEP_FILES = [
    "1단계-구조문맥분석.md",
    "2단계-문헌학적미세분석.md",
    "3단계-신학역사상호본문종합.md",
    "4단계-설교프레임워크.md"
]

def load_prompt(filename):
    path = PROMPT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Bible Analyze 6.0 Browser Automation")
    parser.add_argument("verse", help="Bible verse to analyze")
    args = parser.parse_args()

    print(f"🚀 Starting Browser Agent for: {args.verse}")
    
    # Use a persistent user data directory to save login state
    user_data_dir = "./chrome_data"
    
    with sync_playwright() as p:
        # Launch persistent context (Saves cookies, login sessions)
        # Using channel="chrome" to bypass "secure browser" checks
        print(f"📂 Loading User Profile from: {user_data_dir}")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",  # Force use of Google Chrome
            headless=False,
            ignore_default_args=["--enable-automation"], # Hide automation
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Navigate to Google Gemini
        print("🌍 Navigating to Gemini (https://gemini.google.com/app)...")
        page.goto("https://gemini.google.com/app")
        
        print("\n" + "="*60)
        print("🚦 [CHECKPOINT]")
        print("1. If you are NOT logged in, please log in now.")
        print("2. Make sure the Chat Input box is visible.")
        print("👉 Press ENTER when ready to start automation...")
        print("="*60 + "\n")
        input()
        
        print("🤖 Automation starting...")
        
        combined_report = []
        
        for i, step_file in enumerate(STEP_FILES, 1):
            print(f"⏳ Step {i}: {step_file} processing...", end="", flush=True)
            
            prompt_content = load_prompt(step_file)
            
            if i == 1:
                full_prompt = f"{prompt_content}\n\n분석 대상 본문: [{args.verse}]"
            else:
                full_prompt = prompt_content
            
            try:
                # Robust Selector Strategy
                # 1. Try get_by_role (most accessible/standard)
                # 2. Try generic selectors
                
                # Wait for input to be ready
                # Gemini often changes classes, but role="textbox" is usually stable
                input_locator = page.get_by_role("textbox").nth(0) 
                # Or rich-textarea fallback
                if not input_locator.is_visible(timeout=5000):
                    input_locator = page.locator("div[contenteditable='true']").first
                
                input_locator.wait_for(state="visible", timeout=10000)
                input_locator.click()
                
                # Clear existing text just in case (optional, risky if multiline)
                # page.keyboard.press("Meta+A")
                # page.keyboard.press("Backspace")

                # Type/Paste content
                # Use clipboard for speed and reliability with large text
                # Fix: Use explicit arrow function for arguments
                page.evaluate("text => navigator.clipboard.writeText(text)", full_prompt)
                page.keyboard.press("Meta+V") # Mac Command+V
                
                time.sleep(1) # Visual confirmation
                page.keyboard.press("Enter")
                
                print(" ✅ Sent.")
                
                # Wait for generation completion logic
                print(f"👀 Step {i} Generation in progress...")
                print(f"👉 When finished, click the 'COPY' icon (or select & copy text) in the browser.")
                input(f"👉 Then Press ENTER here to capture the result...")

                # Capture Clipboard (Mac specific 'pbpaste')
                # This reads whatever the user just copied
                try:
                    import subprocess
                    clipboard_content = subprocess.check_output(['pbpaste']).decode('utf-8')
                    print(f"   📝 Captured {len(clipboard_content)} characters.")
                    
                    combined_report.append(f"## Step {i} Result\n\n{clipboard_content}\n\n---\n")
                    
                except Exception as e:
                    print(f"   ⚠️ Failed to read clipboard: {e}")
                    print("   (Continuing without saving this step's output)")

            except Exception as e:
                print(f"\n❌ Error in Step {i}: {e}")
                print("💡 Tip: If selector failed, try clicking the input box manually before retrying.")
                break
        
        # Save Report
        if combined_report:
            output_dir = Path("output/Bible")
            output_dir.mkdir(parents=True, exist_ok=True)
            safe_verse = args.verse.replace(":", "-").replace(" ", "_")
            output_file = output_dir / f"{safe_verse}_browser_analyze.md"
            
            final_content = f"# {args.verse} 분석 리포트 (Browser)\n\n" + "\n".join(combined_report)
            output_file.write_text(final_content, encoding="utf-8")
            
            print("\n" + "="*50)
            print(f"🎉 All steps completed!")
            print(f"📄 Report Saved: {output_file}")
            print("="*50)
            
        input("Press Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    main()
