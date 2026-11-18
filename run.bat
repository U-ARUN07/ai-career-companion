@echo off
cd /d "%~dp0"
echo ======================================================================
echo   IntelliIntern AI - Unified RAG Career Intelligence Platform
echo ======================================================================
echo   Platform:     Infosys Springboard VIP 7.0
echo   Web Portal:   http://localhost:8000
echo   Swagger Docs: http://localhost:8000/docs
echo ======================================================================

:: Free port 8000 if occupied by a previously running process
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Freeing port 8000 from stale process PID %%a...
    taskkill /f /pid %%a >nul 2>&1
)

:: Automatically open browser in 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

echo Server is running! Press Ctrl+C in this window to stop.
echo ======================================================================
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
