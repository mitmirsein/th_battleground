
from src.translator import GlossaryManager

def test_lookup():
    gm = GlossaryManager()
    
    # Test Cases
    queries = ["AA", "ZNW", "TRE"]
    
    for q in queries:
        print(f"\nSearching for: '{q}'")
        try:
            results = gm.lookup(q)
        except Exception as e:
            print(f"Error: {e}")
            continue
            
        if results:
            for r in results:
                print(f"✅ Found: {r.get('canonical', {}).get('ko')} ({r.get('type', 'term')})")
                if r.get('type') == 'journal':
                    print(f"   Desc: {r.get('definitions', {}).get('ko')}")
        else:
            print("❌ Not found")

if __name__ == "__main__":
    test_lookup()
