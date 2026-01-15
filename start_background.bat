@echo off
REM NQ AI Alert System - Background Launcher
REM This script starts the server in a hidden background window

echo ===================================================
echo 🚀 NQ AI Alert System - Starting in Background
echo ===================================================

REM Kill any existing Python processes for NQ
taskkill /F /FI "WINDOWTITLE eq NQ AI Alert System*" 2>nul

REM Start the server from PROJECT ROOT (not backend directory)
REM This is critical for imports to work
start "NQ AI Alert System" /MIN cmd /c "cd /d %~dp0 && python backend/main.py"

echo.
echo ✅ NQ Alert System is now running in the background!
echo.
echo To check if it's running:
echo    - Open Task Manager and look for "NQ AI Alert System"
echo    - Visit http://localhost:8001/
echo.
echo To stop it:
echo    - Run: stop_nq_server.bat
echo    - Or close the "NQ AI Alert System" window in Task Manager
echo.

timeout /t 3

REM Test the server
echo Testing server connection...
timeout /t 5
curl http://localhost:8001/ 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Server is running successfully!
) else (
    echo.
    echo ⚠️  Server may still be starting... give it a few more seconds
)

echo.
echo Press any key to exit (server will keep running)...
pause >nul
