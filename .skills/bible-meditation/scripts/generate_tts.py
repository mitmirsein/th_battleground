#!/usr/bin/env python3
import sys
import json
import re
import base64
import requests
from pathlib import Path
from datetime import datetime

# Configuration Paths
VAULT_ROOT = Path("/Users/msn/Desktop/MS_Brain.nosync")
DEV_ROOT = Path("/Users/msn/Desktop/MS_Dev.nosync")
CONFIG_PATH = VAULT_ROOT / ".obsidian/plugins/devotional-voice/data.json"

def load_config():
    """Load Gemini API Key from Obsidian plugin config."""
    if not CONFIG_PATH.exists():
        print(f"❌ Config file not found: {CONFIG_PATH}")
        sys.exit(1)
        
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    api_key = data.get("geminiApiKey")
    if not api_key:
        print("❌ Gemini API Key not found in config.")
        sys.exit(1)
        
    # Use config values
    model = data.get("ttsGeminiModel", "gemini-2.0-flash-exp")
    voice = data.get("ttsGeminiVoice", "Zephyr") or "Zephyr"
    
    return api_key, model, voice

def extract_script(md_path):
    """Extract content between %%TTS-SCRIPT: and %% markers."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    match = re.search(r"%%TTS-SCRIPT:\s*(.*?)%%", content, re.DOTALL)
    if not match:
        print("❌ No TTS script found in file (%%TTS-SCRIPT: ... %%).")
        sys.exit(1)
        
    script = match.group(1).strip()
    return script, content

def generate_audio(api_key, model, voice, text, output_path):
    """Call Gemini API to generate speech."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": text}]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice
                    }
                }
            }
        }
    }
    
    print(f"🎙️ Generating audio using {model} ({voice})...")
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.text}")
        sys.exit(1)
        
    data = response.json()
    
    try:
        # Extract audio data
        bg_audio = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        audio_bytes = base64.b64decode(bg_audio)
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
            
        print(f"✅ Audio saved: {output_path.name}")
        return True
        
    except (KeyError, IndexError) as e:
        print(f"❌ Failed to parse response: {e}")
        # print(json.dumps(data, indent=2))
        return False

def update_markdown(md_path, audio_filename, content):
    """Insert audio link before the script block."""
    link = f"![[{audio_filename}]]"
    
    # Check if link already exists
    if link in content:
        print("ℹ️ Audio link already exists.")
        return

    # Insert before %%TTS-SCRIPT:
    new_content = re.sub(
        r"(%%TTS-SCRIPT:)",
        f"{link}\n\n\\1",
        content
    )
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("📌 Markdown updated with audio link.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_tts.py <markdown_file_path>")
        sys.exit(1)
        
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"❌ File not found: {md_path}")
        sys.exit(1)
        
    # 1. Load Config
    api_key, model, voice = load_config()
    
    # 2. Extract Script
    script, original_content = extract_script(md_path)
    print(f"📜 Extracted script ({len(script)} chars)")
    
    # 3. Generate Audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Devotional_Audio_{timestamp}.wav"
    output_path = md_path.parent / output_filename
    
    success = generate_audio(api_key, model, voice, script, output_path)
    
    # 4. Update Markdown
    if success:
        update_markdown(md_path, output_filename, original_content)

if __name__ == "__main__":
    main()
