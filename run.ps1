Set-Location -Path $PSScriptRoot
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Starting RAG Internship Matching System (Infosys Springboard VIP 7.0)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Web Portal:   http://localhost:8000" -ForegroundColor Yellow
Write-Host "Swagger Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
