#!/usr/bin/env python3
"""
Lectionary Data Extractor
=========================
Extracts scripture readings from 'Year A - All Seasons_25-26.csv' and saves them as monthly CSV files.

Mapping:
- Date: Parsed from 'Calendar Date'
- Old Testament (구약): 'First reading' + 'Psalm'
- New Testament (신약): 'Second reading' + 'Gospel'
- Season (절기): 'Liturgical Date'

Output:
- projects/Kerygma_Daily/data/monthly/YYYY-MM.csv
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
SOURCE_FILE = "/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/data/Year A - All Seasons_25-26.csv"
OUTPUT_DIR = "/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/data/monthly"

import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import calendar
import scrape_daily_readings  # Import the scraper module

# Configuration
SOURCE_FILE = "/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/data/Year A - All Seasons_25-26.csv"
OUTPUT_DIR = "/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/data/monthly"

def parse_date(date_str):
    """Parses 'Nov 30, 2025' to datetime object."""
    try:
        return datetime.strptime(date_str, "%b %d, %Y")
    except ValueError as e:
        print(f"⚠️  Date parsing error: {e} for '{date_str}'")
        return None

def clean_text(text):
    """Removes extra quotes or whitespace."""
    if not text:
        return ""
    return text.strip().replace('"', '')

def get_days_in_month(year, month):
    """Returns a list of date strings for every day in the given month."""
    num_days = calendar.monthrange(year, month)[1]
    days = [datetime(year, month, day).strftime("%Y-%m-%d") for day in range(1, num_days + 1)]
    return days

def main():
    # 1. Fetch Daily Readings from Web
    print("🌍 1. Fetching Daily Readings via Scraper...")
    daily_readings = scrape_daily_readings.fetch_all_daily_readings()
    
    # 2. Read Sunday/Feast Readings from CSV
    print(f"📖 2. Reading Source CSV: {SOURCE_FILE}")
    sunday_data = {}
    
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            start_index = 0
            for i, line in enumerate(lines):
                if line.startswith("Liturgical Date"):
                    start_index = i
                    break
            
            reader = csv.DictReader(lines[start_index:])
            for row in reader:
                cal_date_str = row.get("Calendar Date")
                if not cal_date_str: continue
                
                dt = parse_date(cal_date_str)
                if not dt: continue
                
                date_str = dt.strftime("%Y-%m-%d")
                
                ot = f"{clean_text(row.get('First reading', ''))} / {clean_text(row.get('Psalm', ''))}"
                nt = f"{clean_text(row.get('Second reading', ''))} / {clean_text(row.get('Gospel', ''))}"
                season = clean_text(row.get('Liturgical Date', ''))
                
                # Cleanup
                if ot.startswith(" / "): ot = ot[3:]
                if ot.endswith(" / "): ot = ot[:-3]
                if nt.startswith(" / "): nt = nt[3:]
                if nt.endswith(" / "): nt = nt[:-3]
                
                sunday_data[date_str] = {
                    "구약": ot,
                    "신약": nt,
                    "절기": season
                }
    except FileNotFoundError:
        print(f"❌ Source file not found: {SOURCE_FILE}")
        return

    # 3. Merge and Generate Output
    print("🔄 3. Merging and Generating Monthly Files...")
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Determine range from CSV (approximate)
    if not sunday_data:
        print("❌ No data found in CSV.")
        return
        
    all_dates = sorted(sunday_data.keys())
    start_date = datetime.strptime(all_dates[0], "%Y-%m-%d")
    end_date = datetime.strptime(all_dates[-1], "%Y-%m-%d")
    
    # Iterate month by month
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        month_key = f"{year}-{month:02d}"
        output_path = os.path.join(OUTPUT_DIR, f"{month_key}.csv")
        
        days_in_month = get_days_in_month(year, month)
        monthly_rows = []
        
        for day in days_in_month:
            row = {"date": day, "구약": "", "신약": "", "절기": ""}
            
            # Priority 1: Sunday Data (CSV)
            if day in sunday_data:
                row.update(sunday_data[day])
            
            # Priority 2: Daily Data (Scraper)
            elif day in daily_readings:
                # Heuristic: split 3 citations? usually "Psalm; OT; NT" or "Psalm; Reading"
                # For simplicity, put full text in '구약' and note in '절기'
                citations = daily_readings[day]["citations"]
                row["구약"] = citations
                row["절기"] = "Daily Lectionary"
                
                # Check if it's Sunday but missing in CSV? Unlikely, but scraper fills gaps.
                
            else:
                # No data available (rare if scraper works well)
                pass
                
            monthly_rows.append(row)
            
        # Write File
        if monthly_rows:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "구약", "신약", "절기"])
                writer.writeheader()
                writer.writerows(monthly_rows)
            # print(f"   ✅ Created: {output_path} ({len(monthly_rows)} days)")
            
        # Next month
        if month == 12:
            current_date = datetime(year + 1, 1, 1)
        else:
            current_date = datetime(year, month + 1, 1)

    print(f"🎉 Processing Complete! Files saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
