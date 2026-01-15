@echo off
echo ===================================================
echo 🐳 NQ AI Alert System - Docker Launcher
echo ===================================================

echo.
echo 1. Building and Starting Container...
docker-compose up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker failed to start. Is Docker Desktop running?
    pause
    exit /b
)

echo.
echo ✅ Server is running in the background!
echo    - API: http://localhost:8001
echo    - Logs: Run 'docker-compose logs -f' to see output
echo.
echo 2. Streaming logs (Ctrl+C to stop watching logs, server keeps running)...
echo.
docker-compose logs -f
