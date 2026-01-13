
import sys
import re
import json
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from chunker import chunk_by_paragraph
from translator import translation_archive

# Pre-defined translations for key chunks
KNOWN_TRANSLATIONS = {
    "1.1. Analogie": "유비(Analogie, 그리스어 ἀναλογία, 라틴어 proportio, 바로와 키케로 이후 사용됨; 퀸틸리아누스, 세네카 및 스콜라 철학 전통에서는 외래어 analogia로도 사용됨)는 가장 일반적인 의미에서 서로 다른 사물, 상황 또는 개념 간에 지배하는 일치(similitudo, convenientia, consensio)를 가리키며, 이는 동등성(aequalitas)이나 동일성(identitas)과는 구별된다."
}

def load_ocr_text(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = re.split(r'\n\n--- Page \d+ ---\n\n', content)
    if not parts[0].strip():
        parts = parts[1:]
    return [(i, part) for i, part in enumerate(parts)]

def run_batch_init():
    ocr_path = PROJECT_ROOT / "temp/Analogie_ocr_full.txt"
    target_path = Path("/Users/msn/Desktop/MS_Dev.nosync/data/msn_th_archive/translations/TRE_Analogie_KR.jsonl")
    
    # 1. Clear existing file
    if target_path.exists():
        target_path.unlink()
        print(f"🗑️  Cleared existing file: {target_path}")
        
    print(f"Loading {ocr_path}...")
    pages = load_ocr_text(ocr_path)
    
    # 2. Chunking
    constraints = {"max_chars": 3000, "min_chars": 200} # Smaller min_chars to capture short paras
    body_chunks, fn_chunks = chunk_by_paragraph(pages, constraints, page_offset=625)
    
    all_chunks = body_chunks + fn_chunks
    # Sort by chunk_id to keep order (body then footnote usually mixed, but ID helps)
    # Actually chunk_id is printed_page_seq.
    all_chunks.sort(key=lambda x: x['chunk_id'])
    
    print(f"🧩 Structure: {len(body_chunks)} body chunks, {len(fn_chunks)} footnotes.")
    
    # 3. Save Records
    print("💾 Initializing translation structure...")
    
    count = 0
    for chunk in all_chunks:
        original = chunk['content']
        translation = ""
        
        # Check if we have a known translation
        is_translated = False
        for key, text in KNOWN_TRANSLATIONS.items():
            if key in original:
                translation = text
                is_translated = True
                break
        
        if not is_translated:
            # Placeholder
            translation = f"(번역 대기) {original[:50]}..."
            
        # Metadata
        meta = {
            "chunk_type": chunk.get("chunk_type", "body"),
            "status": "done" if is_translated else "todo"
        }
        
        translation_archive.save_translation(
            "TRE_Analogie",
            chunk["chunk_id"],
            original,
            translation,
            metadata=meta
        )
        count += 1
        
    print(f"✅ Batch processing complete. {count} records saved.")
    print(f"   Target: {target_path}")

if __name__ == "__main__":
    run_batch_init()
