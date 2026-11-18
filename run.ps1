# Infosys Springboard VIP 7.0 - 1-Click Launch Script
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  IntelliIntern AI - Unified Internship Platform (Infosys VIP 7.0)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Candidate:    Arun" -ForegroundColor Green
Write-Host "  Web Portal:   http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Swagger Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

# Free port 8000 if occupied
$occupied = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($occupied) {
    Write-Host "Freeing port 8000 from stale process..." -ForegroundColor Yellow
    $occupied | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

# Open browser after 2 seconds in background
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8000"
} | Out-Null

Write-Host "Server running at http://localhost:8000 (opening in browser)..." -ForegroundColor Green
Write-Host "Press Ctrl+C to terminate server." -ForegroundColor Gray
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
