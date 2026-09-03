@echo off
chcp 65001 > nul
title Estado de Órdenes - Gameplay Alliance
python ga_monitor.py --status
echo.
pause
