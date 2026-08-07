@echo off
title Dr Mahmoud Risha Clinic
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed.
    echo Please install Python from https://python.org and tick "Add Python to PATH", then run this file again.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Setting up for the first time, please wait...
    python -m venv venv
    venv\Scripts\python -m pip install --upgrade pip
    venv\Scripts\pip install -r requirements.txt
)

start "" http://127.0.0.1:5000
echo Clinic system is running. Keep this window open while using the system.
echo To stop it, close this window or run stop_server.bat.
venv\Scripts\python app.py
