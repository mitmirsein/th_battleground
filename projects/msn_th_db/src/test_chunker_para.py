
import sys
import re
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from chunker import chunk_by_paragraph, ChunkType
from models import ChunkRecord

def load_ocr_text(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by page marker
    pages = []
    # Markers are "\n\n--- Page n ---\n\n"
    parts = re.split(r'\n\n--- Page \d+ ---\n\n', content)
    
    # First part is empty if file starts with marker
    if not parts[0].strip():
        parts = parts[1:]
        
    for i, part in enumerate(parts):
        pages.append((i, part))
        
    return pages

def test_chunking():
    ocr_path = PROJECT_ROOT / "temp/Analogie_ocr.txt"
    if not ocr_path.exists():
        print(f"OCR file not found: {ocr_path}")
        return

    print("Loading OCR text...")
    pages = load_ocr_text(ocr_path)
    print(f"Loaded {len(pages)} pages.")
    
    constraints = {
        "max_chars": 2000, # Smaller than production (6000) to force splitting
        "min_chars": 300
    }
    
    print(f"Running chunk_by_paragraph with max_chars={constraints['max_chars']}...")
    body_chunks, fn_chunks = chunk_by_paragraph(pages, constraints, page_offset=625) # TRE Volume 2, p.625 approx
    
    print(f"\nCreated {len(body_chunks)} BODY chunks.")
    print(f"Created {len(fn_chunks)} FOOTNOTE chunks.")
    
    print("\n--- Body Chunk Samples ---")
    for i, chunk in enumerate(body_chunks[:3]):
        print(f"\n[Chunk {chunk['chunk_id']}] (len={len(chunk['content'])})")
        print(chunk['content'][:200] + "...")
        
        # Check if footnotes were removed
        if "[" in chunk['content'] and "]" in chunk['content']:
            print("  Note: Square brackets found.")
            
    print("\n--- Footnote Chunk Samples ---")
    for i, chunk in enumerate(fn_chunks[:5]):
        print(f"\n[Chunk {chunk['chunk_id']}] Marker: {chunk['footnote_marker']}")
        print(chunk['content'][:100] + "...")
        print(f"  Parent: {chunk['parent_chunk_id']}")

if __name__ == "__main__":
    test_chunking()
