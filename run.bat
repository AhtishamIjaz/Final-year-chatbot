@echo off
title MedGPT — AI Medical Assistant Chatbot
color 0B
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║     MedGPT — AI Medical Assistant Chatbot        ║
echo  ║     Telemedicine Platform  ^|  RAG + LLM          ║
echo  ║     University of Azad Jammu ^& Kashmir           ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  Starting backend server...
echo  Open your browser at:  http://localhost:8000
echo.
echo  Press CTRL+C to stop the server.
echo.

cd /d "%~dp0backend"

:: Open browser after 3 seconds
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8000"

:: Start FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
