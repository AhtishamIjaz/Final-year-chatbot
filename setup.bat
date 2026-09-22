@echo off
title MedGPT — Setup
color 0B
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║     MedGPT — AI Medical Assistant Chatbot        ║
echo  ║         Setting Up Project...                    ║
echo  ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0backend"

echo [1/2] Installing Python dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)

echo.
echo [2/2] Ingesting medical knowledge base into ChromaDB...
python ingest.py
if %errorlevel% neq 0 (
    echo.
    echo  WARNING: Ingestion had an issue. Please check backend configuration.
    pause
)

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║   Setup Complete!                               ║
echo  ║   Now run:  run.bat  to start the application   ║
echo  ╚══════════════════════════════════════════════════╝
echo.
pause
