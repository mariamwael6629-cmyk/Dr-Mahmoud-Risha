@echo off
echo ===================================================================
echo  Open this address on the SECOND device (phone / other PC):
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do echo      http://%%a:5000
echo.
echo  Both devices must be on the SAME Wi-Fi / network.
echo ===================================================================
pause
