@echo off
title Gameplay Alliance Monitor
echo ===================================================
echo   Gameplay Alliance - Monitor de Ordenes Abiertas
echo ===================================================
echo Iniciando monitor continuo (chequeo cada 5 minutos)...
echo Puedes minimizar esta ventana.
echo Para detenerlo, presiona Ctrl + C o cierra la ventana.
echo ===================================================
echo.
python ga_monitor.py --loop
pause
