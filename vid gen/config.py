"""Configuration settings for VidGen Prompt Generation and YouTube Uploader."""

import os
from pathlib import Path

# Try loading from .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    # Search for .env in current folder or parent folder
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

# ========= GEMINI CONFIG =========
# Load API key safely from environment (never hardcoded in source control)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.9

ENABLE_WEB_SEARCH = True

# ========= PROMPT SYSTEM RULES =========
PROMPT_COUNT = 4

# CONSTANTS FOR CONSISTENCY
CONSISTENT_CHARACTER = (
    "A stunningly beautiful young woman with long wavy hair, glowing skin, "
    "wearing a white silk pajama set. She looks happy and amazed."
)
CONSISTENT_BACKGROUND = (
    "A simple, neutral beige wall bathed in warm, golden sunlight. "
    "A distinct, sharp diagonal shadow is cast on the wall behind her. Natural, sun-kissed lighting."
)
CAMERA_ANGLE = "A 9:16 cinematic shot, eye-level, perfectly centered composition."

CONTENT_TYPES = [
    "oddly_satisfying_cutting_squishy_toy",
    "squishy_pressing_stress_ball",
    "slime_playing_poking",
    "dream_bed",
    "dream_food",
    "dream_clothes",
    "dream_makeup",
    "dream_pet"
]

COLOR_PALETTES = {
    "basic_brights": ["Bright Red", "Sunshine Yellow", "Royal Blue", "Kelly Green"],
    "sweet_vibrant": ["Hot Pink", "Bright Turquoise", "Vibrant Purple", "Orange"],
    "rainbow_pop": ["Red", "Orange", "Yellow", "Green", "Blue", "Purple"]
}

VIDEO_SPECS = {
    "aspect_ratio": "9:16",
    "duration": "10-15 seconds",
    "loop": "seamless loop where possible",
    "style": "Hyper-realistic, 8k, Unreal Engine 5 render style, bright lighting, viral aesthetics"
}

# ========= FILE OUTPUT =========
OUTPUT_HTML = "prompts.html"

# ========= YOUTUBE CONFIG =========
YT_CATEGORY_ID = "24"  # Entertainment
YT_PRIVACY_STATUS = "private"  # Scheduled videos require private status on upload
