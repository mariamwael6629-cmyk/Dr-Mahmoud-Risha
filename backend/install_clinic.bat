@echo off
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed.
    echo Please install Python from https://python.org and tick "Add Python to PATH", then run this file again.
    pause
    exit /b 1
)

if not exist "venv\Scripts\pythonw.exe" (
    echo Setting up for the first time, please wait...
    python -m venv venv
    venv\Scripts\python -m pip install --upgrade pip
    venv\Scripts\pip install -r requirements.txt
)

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
powershell -NoProfile -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('%STARTUP%\Clinic Server.lnk'); $s.TargetPath='%~dp0run_silent.vbs'; $s.WorkingDirectory='%~dp0'; $s.Save()"
powershell -NoProfile -Command "$w=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); $s=$w.CreateShortcut((Join-Path $d 'Dr Mahmoud Risha Clinic.lnk')); $s.TargetPath='%~dp0open_clinic.vbs'; $s.WorkingDirectory='%~dp0'; $s.Save()"

start "" wscript.exe "%~dp0run_silent.vbs"

echo.
echo Done.
echo - The server will now start automatically every time Windows starts.
echo - A shortcut "Dr Mahmoud Risha Clinic" was placed on your Desktop.
echo   Double-click it any time to open the system.
echo.
pause
