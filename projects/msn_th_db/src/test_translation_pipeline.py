
import sys
import re
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from chunker import chunk_by_paragraph, ChunkType
from translator import glossary_manager

def load_ocr_text(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Split by page marker
    parts = re.split(r'\n\n--- Page \d+ ---\n\n', content)
    if not parts[0].strip():
        parts = parts[1:]
    return [(i, part) for i, part in enumerate(parts)]

def run_test():
    ocr_path = PROJECT_ROOT / "temp/Analogie_ocr_full.txt"
    print(f"Loading {ocr_path}...")
    
    pages = load_ocr_text(ocr_path)
    
    # Chunking
    constraints = {"max_chars": 3000, "min_chars": 300}
    # Using offset 625 (TRE Vol 2 starts around there inside the volume?) 
    # Actually Analogie starts at 625.
    body_chunks, _ = chunk_by_paragraph(pages, constraints, page_offset=625)
    
    # Find target chunk (1.1. Analogie)
    target_chunk = None
    for chunk in body_chunks:
        if "1.1. Analogie" in chunk['content']:
            target_chunk = chunk
            break
            
    if not target_chunk:
        print("Target chunk '1.1. Analogie' not found!")
        return

    print(f"\n✅ Target Chunk Found: {target_chunk['chunk_id']}")
    print("-" * 40)
    print(target_chunk['content'][:500] + "...") # Preview
    print("-" * 40)
    
    # Extract potential terms (simple whitespace split for demo)
    # In real app, we might use NLP or n-gram matching
    # Here we check specific expected terms
    check_terms = ["Analogie", "proportio", "similitudo", "convenientia", "aequalitas", "identitas"]
    
    print("\n🔍 Glossary Lookup Results:")
    found_terms = []
    for term in check_terms:
        results = glossary_manager.lookup(term)
        if results:
            canonical = results[0]['canonical']
            print(f"- {term}: {canonical.get('ko')} (de: {canonical.get('de')}, en: {canonical.get('en')})")
            found_terms.append(results[0])
        else:
            print(f"- {term}: [Not found in Glossary]")
            
if __name__ == "__main__":
    run_test()
