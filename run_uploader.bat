@echo off
setlocal enabledelayedexpansion
title VidGen - YouTube Shorts Uploader

echo ==========================================================
echo            VidGen - YouTube Shorts Uploader
echo ==========================================================
echo.

cd /d "%~dp0vid gen"

if not exist "uploader.py" (
    echo [ERROR] uploader.py could not be found in:
    echo "%~dp0vid gen"
    echo.
    pause
    exit /b 1
)

python uploader.py %*

echo.
echo ==========================================================
pause
