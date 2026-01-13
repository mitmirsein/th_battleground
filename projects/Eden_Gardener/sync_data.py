import json
import re
import datetime
from pathlib import Path

# Paths
KERYGMA_DIR = Path("/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/data")
EDEN_DATA_JS = Path("/Users/msn/Desktop/MS_Dev.nosync/projects/Eden_Gardener/src/js/data.js")

def clean_text(text):
    if not text:
        return ""
    # Remove content in parentheses including the parentheses themselves
    # The regex matches ( followed by any characters that are not ) and then )
    cleaned = re.sub(r'\s*\([^)]+\)', '', text)
    # Clean up multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def sync():
    merged_data = {}
    
    # Process both Jan and Feb if they exist
    json_files = sorted(KERYGMA_DIR.glob("2026-*.json"))
    
    if not json_files:
        print("❌ No Kerygma data files found.")
        return

    for json_path in json_files:
        print(f"Processing {json_path.name}...")
        with open(json_path, "r", encoding="utf-8") as f:
            src_data = json.load(f)
            
        for date, day_data in src_data.items():
            if date == "metadata":
                continue
            
            merged_data[date] = {
                "date": date,
                "ot": {
                    "ref": day_data.get("ot", {}).get("ref", ""),
                    "kor_std": day_data.get("ot", {}).get("kor_std", "")
                },
                "nt": {
                    "ref": day_data.get("nt", {}).get("ref", ""),
                    "kor_std": day_data.get("nt", {}).get("kor_std", "")
                },
                "meditation": {
                    "text": clean_text(day_data.get("meditation", {}).get("content", ""))
                }
            }

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate JS content
    js_content = f"""/** 
 * Eden Gardener - Devotional Data
 * Auto-synced from Kerygma_Daily
 * Generated at: {now_str}
 */

const sampleDevotionals = {json.dumps(merged_data, indent=4, ensure_ascii=False)};

window.EdenData = {{
    getTodayDevotional: () => {{
        const today = new Date().toISOString().split('T')[0];
        // For development, if no today, return Jan 8th
        return sampleDevotionals[today] || sampleDevotionals["2026-01-08"];
    }},
    getDevotional: (date) => {{
        return sampleDevotionals[date] || null;
    }},
    sampleDevotionals
}};
"""

    with open(EDEN_DATA_JS, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"✅ Sync Complete! {len(merged_data)} days synced to {EDEN_DATA_JS.name}")

if __name__ == "__main__":
    sync()
