"""
Bible Analyze 6.0 Pro - API Automation Tool
Author: Gemini Agent
Date: 2025-12-07

Description:
    Automates the 4-step theological analysis workflow using Google Gemini API.
    Reads prompts from "성경구절분석 6.0" directory and generates a consolidated report.

Usage:
    python analyze_api.py "요한복음 1:1"
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = "gemini-2.0-flash-exp" # Or "gemini-1.5-pro" based on access. Using Flash for speed/cost or Pro for quality.
# User requested 3.0 Pro cost estimation but for actual running we use what's available.
# Let's default to a high quality model available.

PROMPT_DIR = Path("성경구절분석 6.0")
OUTPUT_DIR = Path("output/Bible")

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

def estimate_cost(input_tokens, output_tokens):
    # Pricing based on assumed 3.0 Pro / 1.5 Pro rates (User provided $2 input, $12 output)
    input_cost = (input_tokens / 1_000_000) * 2.00
    output_cost = (output_tokens / 1_000_000) * 12.00
    return input_cost + output_cost

def main():
    parser = argparse.ArgumentParser(description="Bible Analyze 6.0 Automation")
    parser.add_argument("verses", nargs='+', help="Bible verses to analyze (e.g., '요한복음 1:1' '창세기 1:1')")
    parser.add_argument("--model", default="gemini-3-pro-preview", help="Gemini Model ID")
    args = parser.parse_args()

    if not API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in .env or environment")
        sys.exit(1)

    # Process verse list (handle comma separation within args)
    target_verses = []
    for v in args.verses:
        target_verses.extend([x.strip() for x in v.split(",") if x.strip()])

    print(f"🚀 Starting Bible Analysis Batch Job")
    print(f"   Target Verses: {len(target_verses)} {target_verses}")
    print(f"   Model: {args.model}")
    print("-" * 50)

    for current_verse in target_verses:
        print(f"\n▶️ analyzing: {current_verse}")
        
        try:
            client = genai.Client(api_key=API_KEY)
            chat = client.chats.create(model=args.model)
            
            total_input_tokens = 0
            total_output_tokens = 0
            
            combined_output = f"# {current_verse} 주해 (성경구절분석 6.0)\n\n"
            combined_output += f"**분석 본문:** {current_verse}\n"
            combined_output += f"**분석 모델:** {args.model}\n\n---\n\n"

            for i, step_file in enumerate(STEP_FILES, 1):
                print(f"   ⏳ Step {i}: {step_file}...", end="", flush=True)
                
                prompt_content = load_prompt(step_file)
                
                # For Step 1, append the verse
                if i == 1:
                    full_prompt = f"{prompt_content}\n\n분석 대상 본문: [{current_verse}]"
                else:
                    full_prompt = prompt_content

                response = chat.send_message(full_prompt)
                
                # Token usage
                if response.usage_metadata:
                    in_tok = response.usage_metadata.prompt_token_count
                    out_tok = response.usage_metadata.candidates_token_count
                    total_input_tokens += in_tok
                    total_output_tokens += out_tok
                
                step_output = response.text
                
                combined_output += f"## Step {i} Result\n\n{step_output}\n\n---\n\n"
                print(" ✅")

            # Save Output
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            safe_verse = current_verse.replace(":", "-").replace(" ", "_")
            output_file = OUTPUT_DIR / f"{safe_verse}_analyze.md"
            output_file.write_text(combined_output, encoding="utf-8")

            # Cost Report
            cost = estimate_cost(total_input_tokens, total_output_tokens)
            
            print(f"   🎉 완료! 저장: {output_file}")
            print(f"   💰 비용: ${cost:.4f}")
            
        except Exception as e:
            print(f"\n   ❌ Error analyzing {current_verse}: {e}")
            
    print("-" * 50)
    print("🏁 Batch Job Completed.")

if __name__ == "__main__":
    main()
