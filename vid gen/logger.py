"""HTML event logger for VidGen automation workflow."""

import os
import datetime
from pathlib import Path

# Paths: Default log file is kept in project root for clean, contained logs
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
LOG_FILE = PROJECT_ROOT / "vidgen_log.html"

# Initialize HTML log file if it does not exist
if not LOG_FILE.exists():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VidGen Automation Log</title>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0e0e0e;
    color: #ffffff;
    padding: 24px;
    max-width: 900px;
    margin: 0 auto;
}
h1 {
    color: #00ffff;
    font-size: 24px;
    margin-bottom: 20px;
    border-bottom: 1px solid #333;
    padding-bottom: 10px;
}
.log {
    margin-bottom: 12px;
    padding: 12px 16px;
    border-radius: 6px;
    background: #1a1a1a;
    border-left: 4px solid #444;
    font-size: 14px;
    line-height: 1.5;
}
.success { border-left-color: #00ff88; }
.error { border-left-color: #ff4444; }
.info { border-left-color: #00aaff; }

.time {
    font-size: 11px;
    color: #888888;
    margin-bottom: 4px;
    font-family: Consolas, monospace;
}
.msg {
    word-break: break-word;
}
pre {
    background: #111;
    padding: 8px;
    border-radius: 4px;
    margin-top: 6px;
    font-size: 12px;
    overflow-x: auto;
}
</style>
</head>
<body>

<h1>VidGen Automation Log</h1>

""")


def log_event(message: str, status: str = "info"):
    """Append a timestamped HTML event block to the log file.

    Parameters:
        message (str): Log message or HTML string.
        status (str): "info" | "success" | "error"
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry_html = f"""<div class="log {status}">
    <div class="time">{timestamp}</div>
    <div class="msg">{message}</div>
</div>
"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry_html)
    except Exception as e:
        print(f"[{timestamp}] [{status.upper()}] {message} (Log write error: {e})")
