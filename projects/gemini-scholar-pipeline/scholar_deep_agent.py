import os
import sys
import argparse
import asyncio
import json
import sqlite3
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
RESULTS_DIR = "results"
DB_PATH = "scholar_kb.db"
os.makedirs(RESULTS_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS papers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  keyword TEXT,
                  title TEXT,
                  link TEXT,
                  snippet TEXT,
                  pub_info TEXT,
                  citation_count INTEGER,
                  year INTEGER,
                  file_path TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

async def run_deep_scholar_search(topic: str):
    """
    Uses Gemini Deep Research to find scholarly papers and mimic the Phase 3 scraping output.
    """
    print(f"📚 Starting Deep Scholar Search for: {topic}")
    
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    # Detailed prompt to act as a Scholar Agent
    prompt = f"""
    You are an expert academic research assistant using Google Scholar.
    
    Task: Find 10-15 high-quality academic papers/books regarding the topic: "{topic}".
    
    For each paper, provide:
    1. Title
    2. Authors & Publication Year
    3. A brief summary (snippet)
    4. Estimated citation count (if available from search context, otherwise mark as -1)
    5. A link to the PDF or Publisher page
    
    Output Format: JSON List of objects.
    Example:
    [
      {{
        "title": "The Theology of Hope",
        "authors": "Jürgen Moltmann",
        "year": 1967,
        "summary": "This seminal work reinterprets eschatology...",
        "citation_count": 5000,
        "link": "https://..."
      }}
    ]
    
    ENSURE the output is invalid JSON. Do not include markdown formatting like ```json ... ```. Just the raw JSON string.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-thinking-exp-1219',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                response_mime_type="application/json" # Request JSON output
            )
        )
        
        # Parse JSON
        try:
            papers = json.loads(response.text)
        except json.JSONDecodeError:
            print("⚠️ API returned non-JSON text. Attemping to parse...")
            # Fallback or simple cleanup could go here
            return False

        # Save to Markdown (results/topic.md) - mimicking legacy format for compatibility
        safe_topic = topic.replace(" ", "_")
        md_filename = os.path.join(RESULTS_DIR, f"{safe_topic}.md")
        
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# Scholar Search Results for '{topic}'\n\n")
            for p in papers:
                f.write(f"## {p.get('title')}\n")
                f.write(f"- **Authors:** {p.get('authors')} ({p.get('year')})\n")
                f.write(f"- **Summary:** {p.get('summary')}\n")
                f.write(f"- **Citations:** {p.get('citation_count')}\n")
                f.write(f"- **Link:** {p.get('link')}\n\n")
                
        print(f"✅ Markdown results saved to: {md_filename}")

        # Save to DB (scholar_kb.db)
        conn = init_db()
        c = conn.cursor()
        count = 0
        for p in papers:
            c.execute("INSERT INTO papers (keyword, title, link, snippet, pub_info, citation_count, year) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (safe_topic, p.get('title'), p.get('link'), p.get('summary'), p.get('authors'), p.get('citation_count'), p.get('year')))
            count += 1
        conn.commit()
        conn.close()
        print(f"💾 Saved {count} papers to Database ({DB_PATH})")
        
        return True

    except Exception as e:
        print(f"❌ Error during Deep Scholar Search: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Gemini Deep Scholar Agent")
    parser.add_argument("topic", help="Research topic")
    args = parser.parse_args()

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY is not set.")
        sys.exit(1)

    asyncio.run(run_deep_scholar_search(args.topic))

if __name__ == "__main__":
    main()
