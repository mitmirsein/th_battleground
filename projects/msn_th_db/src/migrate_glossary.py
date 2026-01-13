
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# Paths
BASE_DIR = Path("/Users/msn/Desktop/MS_Dev.nosync/projects/msn_th_db")
CSV_PATH = Path("/Users/msn/Desktop/MS_Dev.nosync/data/tre_terms.csv")
OLD_GLOSSARY_PATH = BASE_DIR / "config/glossary.json"
NEW_GLOSSARY_PATH = BASE_DIR / "config/glossary_v2.json"

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()

def generate_id(term: str) -> str:
    # Remove special chars and lowercase
    clean = re.sub(r'[^a-zA-Z0-9]', '', term).lower()
    return f"term_{clean}"

def load_csv_data(csv_path: Path) -> Dict[str, Any]:
    terms = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Skip header if exists, assuming header is row 1
        
        for row in reader:
            if len(row) < 5:
                continue
                
            de_term = clean_text(row[0])
            if not de_term:
                continue
                
            en_term = clean_text(row[1])
            fr_term = clean_text(row[2])
            ko_term = clean_text(row[3])
            desc_basic = clean_text(row[4])
            
            # Check for enhanced description in col 7 (index 6)
            desc_enhanced = ""
            if len(row) >= 7:
                desc_enhanced = clean_text(row[6])
                
            final_desc = desc_enhanced if desc_enhanced else desc_basic
            
            term_id = generate_id(de_term)
            
            terms[de_term] = {
                "id": term_id,
                "canonical": {
                    "de": de_term,
                    "en": en_term,
                    "fr": fr_term,
                    "ko": ko_term
                },
                "definitions": {
                    "ko": final_desc
                },
                "source": "TRE_Lemma_CSV",
                "alternatives": {
                    "de": [],
                    "en": [],
                    "ko": []
                }
            }
            
    return terms

def load_old_glossary(json_path: Path) -> Dict[str, Any]:
    if not json_path.exists():
        return {}
        
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Remove meta keys
    return {k: v for k, v in data.items() if not k.startswith('_')}

def merge_glossaries(csv_terms: Dict[str, Any], old_terms: Dict[str, List[str]]) -> Dict[str, Any]:
    merged_terms = csv_terms.copy()
    
    for key, synonyms in old_terms.items():
        # Check if key exists in CSV data (Case sensitive check first, then insensitive)
        target_key = key
        if key not in merged_terms:
            # Try finding case-insensitive match
            found = False
            for k in merged_terms:
                if k.lower() == key.lower():
                    target_key = k
                    found = True
                    break
            
            if not found:
                # Add as new term from old glossary
                term_id = generate_id(key)
                merged_terms[key] = {
                    "id": term_id,
                    "canonical": {
                        "de": key, # Assuming key is primarily DE or primary term
                        "ko": synonyms[0] if synonyms else "" # Start with first synonym as KO candidate
                    },
                    "alternatives": {
                        "ko": synonyms[1:] if synonyms else []
                    },
                    "source": "Old_Glossary"
                }
                continue
        
        # Merge synonyms into alternatives
        existing = merged_terms[target_key]
        
        # Detect languages of synonyms roughly (this is heuristic)
        for syn in synonyms:
            syn = clean_text(syn)
            if not syn: continue
            
            # Simple heuristic: if Korean char exists -> ko, else en/de
            if re.search(r'[가-힣]', syn):
                if syn != existing["canonical"].get("ko") and syn not in existing["alternatives"]["ko"]:
                    existing["alternatives"]["ko"].append(syn)
            else:
                # Assume EN for now as most old glossary synonyms were EN/DE mix
                if "en" not in existing["alternatives"]:
                    existing["alternatives"]["en"] = []
                if syn != existing["canonical"].get("en") and syn not in existing["alternatives"]["en"]:
                    existing["alternatives"]["en"].append(syn)

    return merged_terms

def main():
    print(f"Loading CSV from {CSV_PATH}...")
    csv_data = load_csv_data(CSV_PATH)
    print(f"Loaded {len(csv_data)} terms from CSV.")
    
    print(f"Loading old glossary from {OLD_GLOSSARY_PATH}...")
    old_data = load_old_glossary(OLD_GLOSSARY_PATH)
    print(f"Loaded {len(old_data)} terms from old glossary.")
    
    print("Merging data...")
    final_terms = merge_glossaries(csv_data, old_data)
    
    # Construct final v2 structure
    final_json = {
        "_meta": {
            "version": "2.0",
            "type": "translation_glossary",
            "updated": "2026-01-13",
            "total_terms": len(final_terms),
            "sources": ["TRE_Lemma_CSV", "Old_Glossary"]
        },
        "terms": final_terms
    }
    
    print(f"Saving to {NEW_GLOSSARY_PATH}...")
    with open(NEW_GLOSSARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, indent=2, ensure_ascii=False)
        
    print("Done!")

if __name__ == "__main__":
    main()
