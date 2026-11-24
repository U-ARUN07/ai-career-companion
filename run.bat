@echo off
title AI Career Companion - 1-Click Full-Stack Launcher
cd /d "%~dp0"

echo =================================================================
echo   AI Career Companion Agent - 1-Click Launcher (All 8 Modules)
echo =================================================================

powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1"

pause
