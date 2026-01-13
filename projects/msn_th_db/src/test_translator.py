
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from translator import glossary_manager

def test_lookup():
    queries = ["Abendmahl", "Analogie", "Justification", "칭의"]
    
    print(f"Glossary loaded: {len(glossary_manager.terms)} terms.")
    
    for q in queries:
        print(f"\nLooking up: {q}")
        results = glossary_manager.lookup(q)
        if not results:
            print("  Not found.")
            continue
            
        for r in results:
            print(f"  Found: {r['canonical'].get('de')} / {r['canonical'].get('ko')}")
            print(f"  Def: {r.get('definitions', {}).get('ko')}")

if __name__ == "__main__":
    test_lookup()
