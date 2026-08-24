@echo off
netsh advfirewall firewall add rule name="Clinic Server 5000" dir=in action=allow protocol=TCP localport=5000
echo.
echo Done. The second device on the same network can now reach this PC on port 5000.
echo (Run this file once, as Administrator.)
pause
