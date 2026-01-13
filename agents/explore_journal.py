#!/usr/bin/env python3
"""
Test script to explore VR eLibrary structure (with Cloudflare bypass)
"""
import sys
sys.path.insert(0, '/Users/msn/Desktop/MS_Dev.nosync/agents')

from tools.browser import BrowserAgent
import json

# Test: Open KuD journal page and get structure
browser = BrowserAgent("explore_kud")

# KuD Band 85, Heft 6
url = "https://www.vr-elibrary.de/toc/kud/85/6"

print(f"🔍 Exploring: {url}")
browser.open(url)

# Wait longer for Cloudflare to pass
print("⏳ Waiting for page load (10 seconds)...")
browser.wait(10000)  # 10 seconds

# Get snapshot
snapshot = browser.snapshot()

# Save raw snapshot for analysis
with open('/Users/msn/Desktop/MS_Dev.nosync/agents/data/kud_snapshot.json', 'w') as f:
    json.dump(snapshot, f, indent=2)

print("✅ Snapshot saved")

# Print summary
if snapshot.get("success"):
    refs = snapshot.get("data", {}).get("refs", {})
    print(f"\n📊 Found {len(refs)} interactive elements")
    
    # Show full snapshot text
    snapshot_text = snapshot.get("data", {}).get("snapshot", "")
    print(f"\n📄 Page structure:\n{snapshot_text[:1500]}")
    
    # Sample first 20 refs
    print(f"\n🔍 First 20 elements:")
    for i, (ref_id, elem) in enumerate(list(refs.items())[:20]):
        role = elem.get("role", "unknown")
        name = elem.get("name", "")[:80]
        print(f"  {ref_id}: [{role}] {name}")

browser.close()
