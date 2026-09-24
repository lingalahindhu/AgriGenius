@echo off
title Launch AgriGenius
cd /d "%~dp0"
echo ============================================================
echo Starting AgriGenius Platform (Backend + Frontend)
echo ============================================================
set "VENV_ACTIVATE="
if exist ".venv\Scripts\activate.bat" (
    set "VENV_ACTIVATE=call .venv\Scripts\activate.bat && "
)

start "AgriGenius Backend" cmd /k "%VENV_ACTIVATE%python -m uvicorn backend.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "AgriGenius Frontend" cmd /k "%VENV_ACTIVATE%python -m streamlit run frontend/app.py --server.port 8501"
echo.
echo Both servers launched in separate windows!
echo Backend API:  http://127.0.0.1:8000
echo Frontend UI:  http://localhost:8501
echo.
