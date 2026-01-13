#!/usr/bin/env python3
"""
Scholar KB Monitor
- Continuously refreshes and shows stats from scholar_kb.db
- Useful for monitoring long-running ingestion/extraction jobs.
"""
import sqlite3
import time
import sys
import os
from datetime import datetime

DB_PATH = "scholar_kb.db"

def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Papers Count
        cursor.execute("SELECT count(*) FROM papers")
        total_papers = cursor.fetchone()[0]
        
        # Web Ref Count (source_type='web_reference')
        # Check if column exists first (migration handled in manager but let's be safe)
        try:
            cursor.execute("SELECT count(*) FROM papers WHERE source_type='web_reference'")
            web_refs = cursor.fetchone()[0]
        except:
            web_refs = "N/A"

        # Facts Count
        try:
            cursor.execute("SELECT count(*) FROM facts")
            total_facts = cursor.fetchone()[0]
        except:
            total_facts = 0
            
        conn.close()
        return total_papers, web_refs, total_facts
    except Exception as e:
        return f"Error: {e}", 0, 0

def main():
    print(f"📊 Scholar KB Monitor (Ctrl+C to exit)")
    print(f"📡 Watching: {DB_PATH}\n")
    
    start_time = datetime.now()
    
    try:
        while True:
            papers, web, facts = get_stats()
            elapsed = datetime.now() - start_time
            
            # Clear line and print status
            # Using carriage return \r to overwrite line
            status = (
                f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                f"Elapsed: {str(elapsed).split('.')[0]} | "
                f"📚 Papers: {papers} (Web: {web}) | "
                f"⛏️  Facts: {total_facts if 'total_facts' in locals() else facts}"
            )
            
            sys.stdout.write(status)
            sys.stdout.flush()
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped.")

if __name__ == "__main__":
    main()
