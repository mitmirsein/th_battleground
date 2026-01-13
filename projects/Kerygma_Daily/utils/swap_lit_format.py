import json
import re
import sys

def swap_format(text):
    # Regex to find patterns like: "Sound(Gloss)"
    # We want to transform it to: "Gloss(Sound)"
    # The text usually looks like: "Sound(Gloss) Sound(Gloss). Sound(Gloss)..."
    
    # We use a callback function for regex replacement to handle the swapping
    def replace_match(match):
        sound = match.group(1).strip()
        gloss = match.group(2).strip()
        return f"{gloss}({sound})"

    # Pattern: Any text not containing '(' followed by '(' then any text not containing ')' then ')'
    # Note: Hebrew/Greek sounds don't have parentheses. Glosses might, but usually don't in this dataset.
    # We need to be careful. The format is strictly Sound(...)
    
    # Attempt simple regex first
    new_text = re.sub(r'([^\s\(\).]+)\(([^\)]+)\)', replace_match, text)
    
    # The above regex might be too simple if "Sound" contains spaces (e.g. "호 파이스 무").
    # Let's try a more robust pattern that captures the "Sound" part which is everything before the '('
    # since the last delimiter (space or start).
    # Actually, looking at the data: "웨사무(그리고 그들이 둘 것이다) 엣-쉐미(나의 이름을)"
    # The structure is effectively a list of items separated by spaces or punctuation.
    
    # Better approach might be to capture the whole block `Sound(Gloss)` and swap.
    # The `Sound` part seems to be the transliteration.
    # Pattern:
    # 1. Capture non-parenthesis chars (Sound)
    # 2. Literal '('
    # 3. Capture content inside (Gloss)
    # 4. Literal ')'
    
    # We need to be careful about what precedes the Sound. Usually a space or start of string.
    # But sometimes there is punctuation e.g. "Sound(Gloss)."
    
    # Pattern details:
    # 1. Sound part: ([^\s\(\).,]+(?: [^\s\(\).,]+)*)
    #    - Starts with non-space/non-paren/non-dot
    #    - Can contain internal spaces
    #    - Does NOT convert punctuation like '.' or ',' which are sentence delimiters.
    # 2. "(" literal
    # 3. Gloss part: ([^\)]+)
    # 4. ")" literal
    
    # We use a lookbehind or just match the structure strictly.
    # If we have ". Sound(Gloss)", the "." is separate.
    # regex: `(?<![^\s])` ? No.
    
    # Let's try this:
    # We search for sequences that look like "Sound(Gloss)" where Sound does not contain starting/ending punctuation.
    
    # Actually, simpler: The punctuation marks in this file seem to be primarily '.' acting as sentence limiters.
    # They usually appear as "Sound(Gloss). Sound(Gloss)" OR "Sound(Gloss) Sound(Gloss)."
    # If it is ". Sound(Gloss)", that implies the period was attached to the previous sentence but spaced wrong?
    # No, typically Hebrew/Greek doesn't use '.' like that in transliteration unless it's a delimiter added by the user.
    # In the provided data: "...이스라엘). 와아니..."
    # The period is separated from the previous close paren? No.
    # "이스라엘 자손들 위에). 와아니"
    # Wait, the period is `).`?
    # If so, it is NOT part of the next Sound.
    # BUT `re.sub` continues scanning.
    # If `). ` is consumed/skipped, the next thing is `와아니`.
    
    # If the text is `...이스라엘). 와아니(...)`, 
    # The regex finds `...이스라엘(...)`. Replaces it.
    # Leaving `.` separate.
    # The next match search starts after the previous match.
    # If `.` is not matched, it remains.
    # Then `와아니(...)` is matched.
    # My previous regex `([^\s\(\)]+...)` MATCHED `.` because `.` is not `\s`, `(`, `)`.
    # So I MUST exclude `.` from the allowed characters in Sound.
    
    pattern = r'([^\s\(\).,]+(?: [^\s\(\).,]+)*)\(([^\)]+)\)'
    return re.sub(pattern, replace_match, text)


file_path = 'data/2026-01.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for date_key, entry in data.items():
        if date_key == 'metadata':
            continue
        
        # Process OT
        # if 'ot' in entry and 'kor_lit' in entry['ot']:
        #     entry['ot']['kor_lit'] = swap_format(entry['ot']['kor_lit'])
        #     count += 1
            
        # Process NT
        # if 'nt' in entry and 'kor_lit' in entry['nt']:
        #     old_nt = entry['nt']['kor_lit']
        #     entry['nt']['kor_lit'] = swap_format(old_nt)
        #     count += 1

        # Process Meditation
        if 'meditation' in entry and 'content' in entry['meditation']:
            old_med = entry['meditation']['content']
            
            # STRICT REGEX for Meditation:
            # Captures only Quoted Sound followed by Parenthesized Gloss.
            # Pattern: (['"][^'"]+['"])\s*\(([^\)]+)\)
            # This avoids capturing preceding sentence text.
            
            def replace_med_match(match):
                sound_quoted = match.group(1).strip()
                gloss = match.group(2).strip()
                return f"{gloss}({sound_quoted})"
            
            med_pattern = r"(['\"][^'\"]+['\"])\s*\(([^\)]+)\)"
            entry['meditation']['content'] = re.sub(med_pattern, replace_med_match, old_med)
            count += 1


    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully processed {count} entries.")

except Exception as e:
    print(f"Error: {e}")
