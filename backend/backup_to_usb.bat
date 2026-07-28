@echo off
setlocal enabledelayedexpansion

REM ── Hourly USB backup for the clinic database + uploaded files ──────────
REM Copies backend\database\clinic.db and backend\uploads\ into a timestamped
REM folder on the first removable (USB flash) drive it finds, then prunes
REM backups older than 7 days. Safe to run even when no flash drive is
REM plugged in - it just logs that and exits cleanly instead of erroring,
REM so it's safe to trigger every hour from Task Scheduler unattended.

set "SCRIPT_DIR=%~dp0"
set "DB_SRC=%SCRIPT_DIR%database\clinic.db"
set "UPLOADS_SRC=%SCRIPT_DIR%uploads"
set "LOG_FILE=%SCRIPT_DIR%backup_log.txt"

REM Locale-independent timestamp (regional date formats vary, so %date%/%time% aren't safe)
set "ldt="
for /f "skip=1" %%x in ('wmic os get localdatetime 2^>nul') do if not defined ldt set "ldt=%%x"
if not defined ldt (
    echo [unknown time] FAILED to read system clock via wmic - aborting run. >> "%LOG_FILE%"
    exit /b 1
)
set "TIMESTAMP=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%_%ldt:~8,2%-%ldt:~10,2%-%ldt:~12,2%"
set "STAMP_LOG=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2% %ldt:~8,2%:%ldt:~10,2%:%ldt:~12,2%"

REM Find the first removable (USB flash) drive letter
set "USB_DRIVE="
for /f "skip=1 tokens=1" %%D in ('wmic logicaldisk where "drivetype=2" get deviceid 2^>nul') do (
    if not defined USB_DRIVE if not "%%D"=="" set "USB_DRIVE=%%D"
)

if not defined USB_DRIVE (
    echo [%STAMP_LOG%] No USB flash drive detected - skipped this run. >> "%LOG_FILE%"
    exit /b 0
)

set "DEST_ROOT=%USB_DRIVE%\ClinicBackups"
set "DEST_DIR=%DEST_ROOT%\%TIMESTAMP%"

if not exist "%DEST_ROOT%" mkdir "%DEST_ROOT%" 2>nul
mkdir "%DEST_DIR%" 2>nul

if exist "%DB_SRC%" (
    copy /y "%DB_SRC%" "%DEST_DIR%\clinic.db" >nul
    if errorlevel 1 (
        echo [%STAMP_LOG%] FAILED copying clinic.db to %USB_DRIVE% >> "%LOG_FILE%"
    ) else (
        echo [%STAMP_LOG%] OK clinic.db -^> %DEST_DIR% >> "%LOG_FILE%"
    )
) else (
    echo [%STAMP_LOG%] WARNING clinic.db not found at %DB_SRC%, skipped. >> "%LOG_FILE%"
)

if exist "%UPLOADS_SRC%" (
    robocopy "%UPLOADS_SRC%" "%DEST_DIR%\uploads" /E /NFL /NDL /NJH /NJS /NP >nul
    if errorlevel 8 (
        echo [%STAMP_LOG%] FAILED copying uploads to %USB_DRIVE% >> "%LOG_FILE%"
    ) else (
        echo [%STAMP_LOG%] OK uploads -^> %DEST_DIR%\uploads >> "%LOG_FILE%"
    )
)

REM Keep only the last 7 days of backups on the flash drive so it doesn't fill up
forfiles /p "%DEST_ROOT%" /d -7 /c "cmd /c if @isdir==TRUE rmdir /s /q @path" 2>nul

echo [%STAMP_LOG%] Backup run complete on %USB_DRIVE% >> "%LOG_FILE%"
endlocal
