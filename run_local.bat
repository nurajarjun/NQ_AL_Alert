@echo off
echo ===================================================
echo 🚀 NQ AI Alert System - Local Launcher
echo ===================================================

echo.
echo 1. Checking dependencies...
python -m pip install -r backend/requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies. Please check Python installation.
    pause
    exit /b
)

echo.
echo 2. Starting AI Backend...
echo    - API: http://localhost:8001
echo    - Docs: http://localhost:8001/docs
echo.
echo ⚠️  KEEP THIS WINDOW OPEN! ⚠️
echo.

python backend/main.py

pause
