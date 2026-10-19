@echo off
setlocal enabledelayedexpansion
title VidGen - AI Prompt Generator

echo ==========================================================
echo            VidGen - AI Video Prompt Generator
echo ==========================================================
echo.

cd /d "%~dp0vid gen"

if not exist "promptgen.py" (
    echo [ERROR] promptgen.py could not be found in:
    echo "%~dp0vid gen"
    echo.
    pause
    exit /b 1
)

python promptgen.py %*

echo.
echo ==========================================================
pause
