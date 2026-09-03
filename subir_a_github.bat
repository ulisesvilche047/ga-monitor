@echo off
chcp 65001 > nul
title Subir monitor a GitHub
echo ========================================================
echo   Subiendo el monitor a tu repositorio en GitHub...
echo ========================================================
echo.
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo   ¡LISTO! Los archivos se subieron correctamente.
    echo ========================================================
) else (
    echo ========================================================
    echo   Hubo un detalle. Revisa si te pide autorizar en el navegador.
    echo ========================================================
)
echo.
pause
