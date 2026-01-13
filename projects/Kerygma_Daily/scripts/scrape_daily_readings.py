#!/usr/bin/env python3
"""
Daily Lectionary Scraper
========================
Fetches daily readings from Vanderbilt Divinity Library.
URL: https://lectionary.library.vanderbilt.edu/daily-readings/

Usage:
    import scrape_daily_readings
    data = scrape_daily_readings.fetch_all_daily_readings()
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

URL = "https://lectionary.library.vanderbilt.edu/daily-readings/"

def parse_date(date_text):
    """
    Parses 'Thursday, November 27, 2025:' into '2025-11-27'.
    """
    try:
        # Remove colon and extra spaces
        clean_text = date_text.strip().rstrip(":")
        # Format: "%A, %B %d, %Y"
        dt = datetime.strptime(clean_text, "%A, %B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError as e:
        # print(f"⚠️ Date parse error: {e} for '{date_text}'")
        return None

def fetch_all_daily_readings():
    """
    Fetches the daily readings page and returns a dictionary:
    {
        "2025-11-27": {
            "citations": "Psalm 122; Daniel 9:15-19; James 4:1-10",
            "link": "..."
        },
        ...
    }
    """
    print(f"🌍 Fetching daily readings from {URL}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Network error: {e}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # The structure is flattened lists in ul.readings? Or just li elements?
    # Browser agent showed <li class="reading">...
    
    # Try finding all li.reading
    readings = soup.find_all('li', class_='reading')
    print(f"📦 Found {len(readings)} reading entries.")
    
    data = {}
    
    for li in readings:
        # 1. Extract Date
        date_span = li.find('span', class_='date')
        if not date_span:
            continue
            
        date_str = parse_date(date_span.get_text())
        if not date_str:
            continue
            
        # 2. Extract Readings
        # Weekdays have <span class="verse"> inside <a>
        verse_span = li.find('span', class_='verse')
        if not verse_span:
            continue
            
        # Get text, clean up
        citations = verse_span.get_text(separator=" ").strip()
        # Clean up semicolons and spaces
        citations = re.sub(r'\s+', ' ', citations).strip()
        if citations.endswith(";"):
            citations = citations[:-1]
            
        # 3. Extract metadata (season? link?)
        link_tag = li.find('a')
        link = link_tag['href'] if link_tag else ""
        if not link.startswith("http"):
             link = "https://lectionary.library.vanderbilt.edu/" + link.lstrip("/")
        
        data[date_str] = {
            "citations": citations,
            "link": link
        }
        
    print(f"✅ Parsed {len(data)} daily readings.")
    return data

if __name__ == "__main__":
    # Test run
    d = fetch_all_daily_readings()
    # Print sample
    keys = list(d.keys())
    if keys:
        print(f"Sample ({keys[0]}): {d[keys[0]]}")
        print(f"Sample ({keys[-1]}): {d[keys[-1]]}")
