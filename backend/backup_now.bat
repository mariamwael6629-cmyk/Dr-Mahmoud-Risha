@echo off
REM Manual test run of the USB backup, with on-screen feedback. Plug in the
REM flash drive first, then double-click this file to confirm the backup
REM works before relying on the hourly Task Scheduler trigger.
echo Running clinic backup now...
call "%~dp0backup_to_usb.bat"
echo.
echo Last 5 log lines (backup_log.txt):
powershell -NoProfile -Command "Get-Content -Tail 5 '%~dp0backup_log.txt'" 2>nul
echo.
pause
