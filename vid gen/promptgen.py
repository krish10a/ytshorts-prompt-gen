"""AI Prompt Generator for Viral Satisfying Shorts.

Generates structured, hyper-descriptive 9:16 video prompts using Google Gemini
with persistent concept history to avoid repetition.
"""

import os
import random
import datetime
import time
import json
from pathlib import Path

from google import genai
from google.api_core import exceptions

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    PROMPT_COUNT,
    CONTENT_TYPES,
    COLOR_PALETTES,
    VIDEO_SPECS,
    LLM_TEMPERATURE,
    CONSISTENT_CHARACTER,
    CONSISTENT_BACKGROUND,
    CAMERA_ANGLE,
    OUTPUT_HTML
)

from logger import log_event

# -------------------------------------------------
# PATHS
# -------------------------------------------------

VIDGEN_DIR = Path(__file__).resolve().parent
PROJECT_DIR = VIDGEN_DIR.parent
OUTPUT_PATH = PROJECT_DIR / OUTPUT_HTML

# -------------------------------------------------
# HISTORY MANAGEMENT
# -------------------------------------------------

HISTORY_FILE = VIDGEN_DIR / "prompt_history.json"


def load_history():
    """Load previously generated concepts to prevent repetitive outputs."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_history(history):
    """Save concept history to disk."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        log_event(f"Failed to save concept history: {e}", status="error")


# -------------------------------------------------
# GENERATE PROMPTS FUNCTION
# -------------------------------------------------

def generate_prompts(client, content_type):
    """Call Gemini to generate consistent, high-variety video prompts."""
    log_event(f"Generating video prompts for: {content_type}...")

    prompts = []
    topic_display = content_type.replace('_', ' ').title()

    # Load past concepts to avoid repetition
    full_history = load_history()
    past_concepts = full_history.get(content_type, [])[-12:]  # Retain last 12 for context window

    # Scenario-specific instructions
    action_instructions = {
        "bed": "The girl enters from the LEFT, climbs onto the CENTER bed, lies down, and sleeps happily. (Modify the bed design drastically for each prompt).",
        "food": "The girl holds a NORMAL SIZED cute food item in both hands. She gives it a soft SQUEEZE to show its squishy texture, then takes a bite. (Change the food item drastically).",
        "eat": "The girl holds a NORMAL SIZED cute food item in both hands. She gives it a soft SQUEEZE to show its squishy texture, then takes a bite. (Change the food item drastically).",
        "clothes": "The girl models the outfit, twisting and turning. (Change the fabric/style drastically).",
        "dress": "The girl models the outfit, twisting and turning. (Change the fabric/style drastically).",
    }

    action_instruction = "The girl interacts with the object (pressing/poking). (Change the object material drastically)."
    for key, instruction in action_instructions.items():
        if key in content_type.lower():
            action_instruction = instruction
            break

    palette_keys = list(COLOR_PALETTES.keys())

    for i in range(PROMPT_COUNT):
        # 1. Rotate palettes across variations
        palette_name = palette_keys[i % len(palette_keys)]
        palette_colors = COLOR_PALETTES[palette_name]

        # 2. Build system instruction with anti-repetition memory
        exclusion_list = ", ".join(past_concepts) if past_concepts else "None yet"

        system_prompt = f"""
You are an elite AI Creative Director for viral satisfying videos.

GOAL: Write a RICH, DETAILED, HYPER-DESCRIPTIVE video prompt (~500 words).

MANDATORY CONSISTENCY (DO NOT CHANGE):
1. CHARACTER: {CONSISTENT_CHARACTER}
2. BACKGROUND: {CONSISTENT_BACKGROUND}
3. CAMERA: {CAMERA_ANGLE}
4. ACTION BASE: {action_instruction}

CREATIVE DIRECTION (VARIATION {i+1}):
- TOPIC: {topic_display}
- Vibe: Oddly Satisfying, Squishy, Squeezy, Cute, ASMR.
- Color Inspiration: {palette_name} ({', '.join(palette_colors)}).
- STYLE: BASIC VIBRANT COLORS (Red, Blue, Yellow, Pink). High Saturation.

REFERENCE STYLE (IF "BED"):
- Visualize beds made of GIANT FRUIT SLICES (Kiwi, Orange, Watermelon).
- Visualize beds made of GIANT CANDY (Macaron Stacks, Marshmallows).
- The girl lies ON TOP of these giant food objects.

CRITICAL NOVELTY RULE:
- DO NOT generate these previous concepts: [{exclusion_list}]
- GENERATE A BRAND NEW, UNIQUE CONCEPT.

DETAILS TO INCLUDE:
- Specific textures (velvet, jelly, clouds, sparkling water).
- Specific lighting (Sun-kissed, natural, golden hour, sharp shadows).
- Sound visualisation (describe the visible crunch, squish, or softness).

OUTPUT FORMAT (STRICT):
CONCEPT: <Short Name of the Concept>
PROMPT: <The full ~500 word prompt text>
"""

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=system_prompt,
                config={"temperature": LLM_TEMPERATURE}
            )
            response_text = response.text.strip()

            # Parse structured response
            concept_name = f"Concept {i+1}"
            prompt_text = response_text

            if "CONCEPT:" in response_text and "PROMPT:" in response_text:
                parts = response_text.split("PROMPT:")
                concept_name = parts[0].replace("CONCEPT:", "").strip()
                prompt_text = parts[1].strip()
                past_concepts.append(concept_name)

            final_output = f"[Topic: {topic_display} | Concept: {concept_name}] \n{prompt_text}"
            prompts.append(final_output)

            log_event(f"Generated prompt {i+1}/{PROMPT_COUNT}: {concept_name}")
            time.sleep(1)  # Respect API rate pacing
        except Exception as e:
            log_event(f"Failed to generate prompt {i+1}: {e}", status="error")

    # Update concept history
    full_history[content_type] = past_concepts[-12:]
    save_history(full_history)

    return prompts


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    if not GEMINI_API_KEY:
        print("\n❌ Error: GEMINI_API_KEY is not set.")
        print("Please configure your GEMINI_API_KEY in .env or as an environment variable.")
        print("See .env.example for details.\n")
        log_event("GEMINI_API_KEY missing. Prompt generation halted.", status="error")
        return

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        log_event(f"Failed to initialize Gemini client: {e}", status="error")
        print(f"❌ Failed to initialize Gemini client: {e}")
        return

    # Interactive Content Type Selection
    print("\n✨ VID GEN: Select Content Type ✨")
    print("-----------------------------------")
    for idx, c_type in enumerate(CONTENT_TYPES):
        print(f"{idx + 1}. {c_type.replace('_', ' ').title()}")
    print("-----------------------------------")

    try:
        selection = input(f"Enter number (1-{len(CONTENT_TYPES)}): ").strip()
        idx = int(selection) - 1
        if 0 <= idx < len(CONTENT_TYPES):
            selected_type = CONTENT_TYPES[idx]
        else:
            print("❌ Invalid selection. Defaulting to Random.")
            selected_type = random.choice(CONTENT_TYPES)
    except Exception:
        print("❌ Invalid input. Defaulting to Random.")
        selected_type = random.choice(CONTENT_TYPES)

    print(f"\nSelected: {selected_type}\nGenerating {PROMPT_COUNT} unique prompts...")

    # Cache selection for Uploader
    session_file = VIDGEN_DIR / "current_session.json"
    try:
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump({"last_topic": selected_type}, f)
    except Exception as e:
        log_event(f"Failed to save session topic: {e}", status="error")

    generated_prompts = generate_prompts(client, selected_type)

    if not generated_prompts:
        log_event("No prompts were generated.", status="error")
        print("❌ No prompts were generated. Check error log.")
        return

    prompts_text = ""
    for i, prompt in enumerate(generated_prompts):
        prompts_text += f"{i+1}. {prompt}\n\n"

    # Generate HTML Output
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Video Prompts</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0f0f0f;
    color: #ffffff;
    padding: 32px 16px;
    max-width: 900px;
    margin: 0 auto;
    line-height: 1.6;
}}
h1 {{
    color: #00ffff;
    font-size: 24px;
    margin-bottom: 8px;
}}
.meta {{
    margin-bottom: 24px;
    color: #888888;
    font-size: 13px;
}}
pre {{
    background: #1a1a1a;
    padding: 20px;
    border-radius: 8px;
    white-space: pre-wrap;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid #333;
}}
</style>
</head>
<body>

<h1>AI Video Generation Prompts</h1>

<div class="meta">
<b>Generated:</b> {timestamp}<br>
<b>Content Type:</b> {selected_type.replace('_', ' ').title()}<br>
<b>Strategy:</b> Consistent Character + High-Variety Aesthetic Topics
</div>

<pre>{prompts_text}</pre>

</body>
</html>
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    log_event(f"prompts.html successfully generated at {OUTPUT_PATH}")
    print(f" Prompt generation complete! Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
