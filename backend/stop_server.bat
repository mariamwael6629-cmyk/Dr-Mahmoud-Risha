@echo off
REM Stops the clinic server by finding whichever process is listening on
REM port 5000 and killing it. Use this if you need to restart the server
REM manually instead of waiting for the next reboot.
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do taskkill /F /PID %%a
echo Done.
pause
