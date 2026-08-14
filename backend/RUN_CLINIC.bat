@echo off
cd /d "%~dp0"
title Dr Mahmoud Risha Clinic

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo ===================================================================
    echo  Python is NOT installed yet.
    echo  1^) Go to https://python.org  -^>  Downloads  -^>  Download Python
    echo  2^) Run the installer and TICK the box "Add python.exe to PATH"
    echo  3^) Click "Install Now" and wait until it finishes
    echo  4^) Then double-click this file again.
    echo ===================================================================
    echo.
    pause
    exit /b 1
)

echo Installing required packages, please wait...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

start "" /min cmd /c "timeout /t 6 >nul & start "" http://127.0.0.1:5000"

echo.
echo The clinic system is running. Keep this window open (you can minimize it).
echo Chrome will open in a few seconds. To stop, close this window.
echo.
python app.py
pause
