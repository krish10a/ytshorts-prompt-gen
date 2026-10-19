# YouTube Shorts AI Prompt Generator & Uploader

A local Python workflow to generate structured, consistent 9:16 video generation prompts using Google Gemini and automatically upload rendered videos as YouTube Shorts with generated titles, descriptions, and scheduled publish times.

## What It Does

1. **Prompt Generator (`promptgen.py`):**
   - Prompts for a satisfying video topic (cutting squishy toys, stress balls, dream foods, slime, etc.).
   - Uses Google Gemini (`gemini-2.5-flash`) to generate detailed 9:16 text prompts with consistent character, lighting, camera angles, and textures.
   - Retains a local history (`prompt_history.json`) to prevent repeating previous concepts across runs.
   - Exports the prompts into a clean HTML file (`prompts.html`).

2. **YouTube Shorts Uploader (`uploader.py`):**
   - Picks up rendered video files from `vid gen/shorts/`.
   - Uses Gemini with Google Search tool to generate authentic, non-AI-sounding titles, descriptions, and trending hashtags.
   - Schedules the video for the next 9:00 AM IST slot.
   - Uploads via YouTube Data API v3 and caches credentials in `token.json` for seamless subsequent runs.
   - Archives uploaded files to `vid gen/uploaded/`.

## Files

```text
├── run_promptgen.bat            # One-click launcher for prompt generation
├── run_uploader.bat             # One-click launcher for video uploader
├── prompts.html                 # Sample generated prompts output
├── .env.example                 # Example environment configuration
├── .gitignore                   # Ignores credentials, videos, and logs
├── LICENSE                      # MIT License
└── vid gen/
    ├── config.py                # Model and channel settings
    ├── promptgen.py             # Prompt generation script
    ├── uploader.py              # YouTube upload and scheduling script
    ├── logger.py                # HTML event logger
    ├── requirements.txt         # Python dependencies
    ├── client_secret.json.example  # Google Cloud OAuth template
    ├── shorts/                  # Drop videos here for upload
    └── uploaded/                # Uploaded videos are moved here
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r "vid gen/requirements.txt"
```

### 2. Configure Credentials
1. Copy `.env.example` to `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
2. For YouTube uploading, get an OAuth 2.0 Client Secret from [Google Cloud Console](https://console.cloud.google.com/) (Desktop app type), and save it as:
   ```text
   vid gen/client_secret.json
   ```

### 3. Generate Prompts
Run `run_promptgen.bat` (or `python "vid gen/promptgen.py"`). Choose a category from the menu, and open `prompts.html` to copy your prompts into your video generator.

### 4. Upload a Video
Place your rendered `.mp4` into `vid gen/shorts/` and run `run_uploader.bat` (or `python "vid gen/uploader.py"`).

## Requirements

- Python 3.9+
- Google Gemini API key (Free tier available on Google AI Studio)
- Google Cloud project with YouTube Data API v3 enabled (for auto-uploader)

## License

MIT License