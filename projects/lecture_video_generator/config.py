"""
Lecture Video Generator - Configuration
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Paths
PROJECT_ROOT = Path(__file__).parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Ensure directories exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Gemini Models
OUTLINE_MODEL = "gemini-2.5-flash"
TTS_MODEL = "gemini-2.5-pro-preview-tts"

# TTS Configuration
TTS_VOICE = "Enceladus"

# Slide Configuration
SLIDE_WIDTH = 1920
SLIDE_HEIGHT = 1080

# Slide Colors (from sample)
COLORS = {
    "bg_start": "#1E3A8A",
    "bg_mid": "#0F285A",
    "bg_end": "#0A1A3C",
    "text_main": "#E0E0E0",
    "text_sub": "#A3BFFA",
    "accent": "#D4A017",
    "title": "#FFFFFF",
    "pattern": "#D4A017",
}

# Fonts
FONTS = {
    "title": "Noto Sans KR",  # User requested Noto Sans KR for all
    "body": "Noto Sans KR",
}
