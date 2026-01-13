import json
import re

def count_words(text, lang):
    # Remove cantillation marks/accents for simpler counting if needed, 
    # but strictly splitting by space is a good first proxy.
    # For Hebrew, maqqef (-) connects words, so might need to treat as one or split.
    # Usually in the JSON, words array often separates them or keeps them combined depending on lemma.
    # Let's simple split by space first.
    return len(text.strip().split())

def audit_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mismatches = []
    
    for date, content in data.items():
        if date == "metadata": continue
        
        # Check OT
        ot = content.get('ot', {})
        focus_text = ot.get('focus_text', '')
        words = ot.get('words', [])
        # Hebrew word count (naive split by space)
        # Handle Maqqef (U+05BE) or hyphen generally treated as connected in text but maybe separate in parsing?
        # Actually usually parsing follows the whitespace structure or breaks it down further.
        # If words array is SMALLER than whitespace-split text, definitely missing.
        
        ft_count = len(focus_text.strip().split())
        w_count = len(words)
        
        if ft_count > w_count:
            mismatches.append(f"{date} OT (Heb): Focus Text {ft_count} words vs Parsed {w_count} words")
            
        # Check NT
        nt = content.get('nt', {})
        focus_text_nt = nt.get('focus_text', '')
        words_nt = nt.get('words', [])
        
        ft_count_nt = len(focus_text_nt.strip().split())
        w_count_nt = len(words_nt)
        
        if ft_count_nt > w_count_nt:
            mismatches.append(f"{date} NT (Grk): Focus Text {ft_count_nt} words vs Parsed {w_count_nt} words")
            
    return mismatches

mismatches = audit_json('/Users/msn/Desktop/MS_Dev.nosync/projects/Kerygma_Daily/data/2026-01.json')
for m in mismatches:
    print(m)
