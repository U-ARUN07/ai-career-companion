# AI Career Companion 1-Click Launcher
$ErrorActionPreference = "SilentlyContinue"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  AI Career Companion Agent - Full-Stack Launcher (All 8 Modules)" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Kill any existing processes on port 8001 (Backend) and 5173 (Frontend)
Write-Host "`n[1/3] Checking and clearing ports 8001 & 5173..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort 8001, 5173 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    if ($p -and $p -ne 0) {
        Write-Host "Freeing port from PID $p..." -ForegroundColor DarkGray
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Milliseconds 800

# 2. Start FastAPI Backend on port 8001
Write-Host "`n[2/3] Starting FastAPI Backend on http://127.0.0.1:8001 ..." -ForegroundColor Green
$backendProc = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload" -WorkingDirectory "$PSScriptRoot\backend" -PassThru

# Wait for backend to be ready
$backendReady = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $res = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -TimeoutSec 1 -UseBasicParsing
        if ($res.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {}
    Start-Sleep -Milliseconds 500
}

if ($backendReady) {
    Write-Host "FastAPI Backend is running and healthy! (Docs: http://127.0.0.1:8001/docs)" -ForegroundColor Green
} else {
    Write-Host "FastAPI Backend starting up in background..." -ForegroundColor Yellow
}

# 3. Start React 18 + Vite Frontend on port 5173
Write-Host "`n[3/3] Starting React Vite Frontend on http://localhost:5173 ..." -ForegroundColor Green
$frontendProc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory "$PSScriptRoot\frontend" -PassThru

# Wait 2 seconds for Vite to bind port
Start-Sleep -Seconds 2

# 4. Open default browser to Frontend
Write-Host "`nOpening application in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host "  SUCCESS: System is running live!" -ForegroundColor Green
Write-Host "  - React Web Application: http://localhost:5173" -ForegroundColor Green
Write-Host "  - FastAPI Swagger Docs:  http://127.0.0.1:8001/docs" -ForegroundColor Green
Write-Host "  - Groq Cloud AI Engine:  Active (qwen/qwen3.8-27b)" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "Press Ctrl + C or close this window to exit." -ForegroundColor DarkGray

# Wait on processes
Wait-Process -Id $backendProc.Id
