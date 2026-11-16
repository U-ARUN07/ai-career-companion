@echo off
cd /d "%~dp0"
echo ======================================================================
echo Starting RAG Internship Matching System (Infosys Springboard VIP 7.0)
echo ======================================================================
echo Web Portal:    http://localhost:8000
echo Swagger Docs:  http://localhost:8000/docs
echo ======================================================================
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
