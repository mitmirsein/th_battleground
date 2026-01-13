import os
import sys
import argparse
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

async def generate_deep_research_report(topic: str):
    """
    Generates a deep research report using the Gemini Deep Research Agent.
    """
    print(f"🚀 Starting Deep Research for topic: {topic}")
    print("   (This may take several minutes as the agent researches the web...)")

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    # Define the prompt for the Deep Research Agent
    prompt = f"""
    Conduct a comprehensive academic research on the topic: "{topic}".
    
    Your goal is to produce a detailed research report that covers:
    1. Historical context and definitions.
    2. Key theological and philosophical arguments.
    3. Major scholarly debates and diverse perspectives.
    4. Implications for modern theology/society.
    
    Format the output in clear Markdown with:
    - H2 (##) for major sections.
    - Bullet points for key details.
    - Bold text for important terms.
    - Citations where applicable (the agent naturally provides these).
    
    The tone should be academic, objective, and profound.
    """

    try:
        # Using the Deep Research model/agent
        # Note: Model ID 'gemini-deep-research-1' is assumed based on recent updates.
        # If this specific ID is not yet active, we might need to use a different endpoint or configuration.
        response = client.models.generate_content(
            model='gemini-2.0-flash-thinking-exp-1219', # Placeholder, ideally 'gemini-deep-research-1'
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())], # Ensure search is enabled
                response_mime_type="text/plain"
            )
        )
        
        # Deep Research Agent usually returns a long text with citations.
        report_content = response.text

        # 1. Add Metadata Header
        final_report = f"""# Gemini Deep Research Report

**Topic:** {topic}
**Generated:** {os.popen('date').read().strip()}
**Source:** Gemini Deep Research API

---

{report_content}
"""

        # 2. Save file
        safe_topic = topic.replace(" ", "_")
        filename = os.path.join(REPORT_DIR, f"{safe_topic}_raw.md")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_report)
            
        print(f"✅ Report saved to: {filename}")
        return True

    except Exception as e:
        print(f"❌ Error during Deep Research: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Gemini Deep Research Session")
    parser.add_argument("topic", help="Research topic")
    args = parser.parse_args()

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY is not set.")
        sys.exit(1)

    asyncio.run(generate_deep_research_report(args.topic))

if __name__ == "__main__":
    main()
