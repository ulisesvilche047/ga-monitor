@echo off
chcp 65001 > nul
title Probar Notificación Push
echo ===================================================
echo   Enviando notificación push de prueba al celular...
echo ===================================================
python ga_monitor.py --test-notification
echo.
pause
