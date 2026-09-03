@echo off
title Probar Notificacion Push
echo ===================================================
echo   Enviando notificacion push de prueba al celular...
echo ===================================================
python ga_monitor.py --test-notification
echo.
pause
