@echo off
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed.
    echo Please install Python from https://python.org and tick "Add Python to PATH", then run this file again.
    pause
    exit /b 1
)

if exist "venv" rmdir /s /q "venv"

echo Installing, please wait...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
powershell -NoProfile -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('%STARTUP%\Clinic Server.lnk'); $s.TargetPath='%~dp0run_silent.vbs'; $s.WorkingDirectory='%~dp0'; $s.Save()"
powershell -NoProfile -Command "$w=New-Object -ComObject WScript.Shell; $d=[Environment]::GetFolderPath('Desktop'); $s=$w.CreateShortcut((Join-Path $d 'Dr Mahmoud Risha Clinic.lnk')); $s.TargetPath='%~dp0open_clinic.vbs'; $s.WorkingDirectory='%~dp0'; $s.Save()"

start "" wscript.exe "%~dp0run_silent.vbs"

echo.
echo Done.
echo - The server will start automatically every time Windows starts.
echo - A shortcut "Dr Mahmoud Risha Clinic" was placed on your Desktop.
echo.
pause
