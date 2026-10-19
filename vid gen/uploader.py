"""YouTube Shorts Automation Uploader.

Generates SEO-optimized metadata and tags using Gemini, schedules videos for
optimal publishing windows, and uploads directly via the YouTube Data API v3.
"""

import os
import datetime
import shutil
import time
import json
from pathlib import Path

import pytz
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_TEMPERATURE,
    YT_CATEGORY_ID,
    YT_PRIVACY_STATUS,
    ENABLE_WEB_SEARCH
)

from logger import log_event

# -------------------------------------------------
# PATHS
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

SHORTS_DIR = BASE_DIR / "shorts"
UPLOADED_DIR = BASE_DIR / "uploaded"
CLIENT_SECRET = BASE_DIR / "client_secret.json"
TOKEN_FILE = BASE_DIR / "token.json"

os.makedirs(SHORTS_DIR, exist_ok=True)
os.makedirs(UPLOADED_DIR, exist_ok=True)

# -------------------------------------------------
# YOUTUBE AUTH
# -------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_client():
    """Authenticate and return an authorized YouTube Data API v3 client."""
    creds = None

    # Load cached access/refresh token if present
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            log_event(f"Cached token read warning: {e}", status="info")
            creds = None

    # Refresh expired credentials or trigger local OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                log_event(f"Token refresh failed, re-authenticating: {e}", status="info")
                creds = None

        if not creds:
            if not CLIENT_SECRET.exists():
                raise FileNotFoundError(
                    f"client_secret.json not found in {BASE_DIR}.\n"
                    "Please download your OAuth client credentials from Google Cloud Console "
                    "or refer to client_secret.json.example."
                )

            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)

        # Cache refreshed token for subsequent unattended runs
        try:
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception as e:
            log_event(f"Could not cache token: {e}", status="info")

    return build("youtube", "v3", credentials=creds)


# -------------------------------------------------
# PARSE METADATA
# -------------------------------------------------

def parse_metadata(text: str):
    """Parse Gemini-generated structured text into title, description, and hashtags."""
    title = "My Satisfying Video"
    description = "Relaxing visuals for you. #shorts"
    hashtags = "#Shorts #Satisfying"

    # Normalize bold formatting
    text = (
        text.replace("**TITLE:**", "TITLE:")
        .replace("**DESCRIPTION:**", "DESCRIPTION:")
        .replace("**HASHTAGS:**", "HASHTAGS:")
    )

    current_section = None
    parsed_title = ""
    parsed_desc = ""
    parsed_tags = ""

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.upper().startswith("TITLE:"):
            parsed_title = line[6:].strip()
            current_section = "TITLE"
        elif line.upper().startswith("DESCRIPTION:"):
            current_section = "DESCRIPTION"
            val = line[12:].strip()
            if val:
                parsed_desc += val + "\n"
        elif line.upper().startswith("HASHTAGS:"):
            parsed_tags = line[9:].strip()
            current_section = "HASHTAGS"
        else:
            if current_section == "DESCRIPTION":
                parsed_desc += line + "\n"
            elif current_section == "TITLE" and not parsed_title:
                parsed_title = line
            elif current_section == "HASHTAGS":
                parsed_tags += line + " "

    if parsed_title:
        title = parsed_title
    if parsed_desc:
        description = parsed_desc
    if parsed_tags:
        hashtags = parsed_tags

    # YouTube title constraint: maximum 100 characters
    return title[:95], description.strip(), hashtags


# -------------------------------------------------
# MAIN UPLOAD ROUTINE
# -------------------------------------------------

def main():
    if not SHORTS_DIR.exists():
        log_event(f"Shorts directory not found: {SHORTS_DIR}", status="error")
        return

    # Check for pending videos
    videos = [f for f in os.listdir(SHORTS_DIR) if f.lower().endswith((".mp4", ".mov", ".mkv"))]

    if len(videos) == 0:
        log_event("No video files found in 'vid gen/shorts/' folder to upload.", status="info")
        print("ℹ️  No pending videos found in 'vid gen/shorts/'. Place an MP4 video there to upload.")
        return

    if len(videos) > 1:
        log_event(f"Warning: Multiple videos found ({len(videos)}). Processing first file: {videos[0]}", status="info")

    video_file = videos[0]
    video_path = SHORTS_DIR / video_file

    log_event(f"Found video ready for upload: <b>{video_file}</b>")

    # Initialize Gemini client for metadata generation
    if not GEMINI_API_KEY:
        log_event("GEMINI_API_KEY is not configured.", status="error")
        print("❌ Error: GEMINI_API_KEY not configured in .env or environment.")
        return

    try:
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        log_event(f"Failed to initialize Gemini client: {e}", status="error")
        return

    # Read context from previous prompt generation session
    topic_context = "Satisfying Dream Objects"
    session_file = BASE_DIR / "current_session.json"
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                topic_context = data.get("last_topic", topic_context).replace("_", " ").title()
        except Exception:
            pass

    metadata_prompt = f"""You are an expert YouTube Shorts growth strategist.

TASK:
Generate viral, high-retention metadata for a "Question/Choice" style satisfying video.
You MUST use Google Search to find current top trending hashtags.

VIDEO CONTEXT:
A video presenting: {topic_context}.
The video focuses on the satisfying visual textures and ASMR aesthetics of this object.

OFF-LIMITS WORDS (STRICT):
Do NOT use: "AI", "Artificial Intelligence", "Generated", "Robot", "Computer", "Simulation".
Make it feel organic, authentic, and real.

OUTPUT FORMAT (STRICT):
TITLE:
<Write a standard Sentence Case question? Add a relevant emoji. MUST end with #shorts>
(Example: Which Unreal Bed Would You Pick? 🥝 #shorts)

DESCRIPTION:
<Engage the viewer immediately. "Option A or Option B? Tell me in the comments!" Describe the texture/vibes. End with "Subscribe for more dream choices! ✨">

HASHTAGS:
<Provide a list of EXACTLY 20 trending hashtags. Separate with spaces. Start with #Shorts #Satisfying #POV #DreamLife>"""

    def call_gemini(prompt: str) -> str:
        config_params = {"temperature": LLM_TEMPERATURE}
        if ENABLE_WEB_SEARCH:
            config_params['tools'] = [{'google_search': {}}]

        response = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config_params
        )
        return response.text.strip()

    try:
        print("Generating viral metadata via Gemini...")
        metadata_text = call_gemini(metadata_prompt)
    except Exception as e:
        log_event(f"Gemini metadata generation failed: {e}", status="error")
        print(f"❌ Gemini metadata generation failed: {e}")
        return

    if not metadata_text:
        log_event("Gemini metadata generation returned empty text.", status="error")
        return

    title, description, hashtags = parse_metadata(metadata_text)
    log_event(f"Generated title: <b>{title}</b>")
    print(f" Title: {title}")

    # Format tags for YouTube API
    tags_list = [tag.replace("#", "") for tag in hashtags.split() if tag.strip()][:25]

    # Calculate optimal scheduled publish time (9:00 AM IST)
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.datetime.now(ist)
    publish_date = now_ist.replace(hour=9, minute=0, second=0, microsecond=0)

    if now_ist.hour >= 9:
        publish_date += datetime.timedelta(days=1)

    publish_date_utc = publish_date.astimezone(pytz.utc).isoformat()
    log_event(f"Scheduled for: <b>{publish_date.strftime('%Y-%m-%d 09:00 IST')}</b>")

    # Connect to YouTube
    print("Authenticating with YouTube API...")
    try:
        youtube = get_youtube_client()
    except Exception as e:
        log_event(f"Failed to authenticate with YouTube: {e}", status="error")
        print(f"❌ YouTube authentication error: {e}")
        return

    print("Uploading video payload to YouTube...")
    log_event("Uploading video to YouTube...")

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": f"{description}\n\n{hashtags}",
                    "tags": tags_list,
                    "categoryId": YT_CATEGORY_ID,
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": YT_PRIVACY_STATUS,
                    "publishAt": publish_date_utc,
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        )
        response = request.execute()
        del request
    except Exception as e:
        log_event(f"Upload failed: {e}", status="error")
        print(f"❌ Upload failed: {e}")
        return

    video_id = response.get("id")
    if not video_id:
        log_event("Upload finished without returning a Video ID.", status="error")
        return

    log_event(f"Upload successful! Video ID: <b>{video_id}</b>", status="success")
    print(f" Upload successful! Video ID: {video_id}")

    # Move processed video to uploaded archive
    dest_path = UPLOADED_DIR / video_file
    max_retries = 5

    for attempt in range(max_retries):
        try:
            shutil.move(str(video_path), str(dest_path))
            log_event(f"Video archived to uploaded/: <b>{video_file}</b>", status="success")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                log_event(f"Could not archive video to uploaded/: {e}", status="error")

    print(" Automation run complete. Check vidgen_log.html for full audit trace.")


if __name__ == "__main__":
    main()
