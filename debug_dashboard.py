from agents.convoy import ConvoyAgent
from pathlib import Path
import sys

print("🏎️ Force Updating Dashboard...")
try:
    agent = ConvoyAgent(role='WORKER')
    print(f"📍 Target Dir: {agent.convoy_dir}")
    
    files = list(agent.convoy_dir.glob("*.*"))
    print(f"📂 Found {len(files)} files.")
    
    for f in files:
        if f.name == 'index.html' or f.suffix not in ['.json', '.md']: continue
        print(f"   Reading {f.name}...", end="")
        res = agent._read_task(f) # 복구됨
        if res:
            print(" OK")
            if 'filename' in res and res['filename'] == 'obsidian.md':
                print(f"      -> Found obsidian.md with status: {res.get('status')}")
        else:
            print(" FAIL (None returned)")
            
    agent._update_dashboard()
    print("✅ Dashboard Updated.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
