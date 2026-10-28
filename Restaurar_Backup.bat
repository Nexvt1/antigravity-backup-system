@echo off
title Restaurador de Backups do Antigravity
chcp 65001 > nul
cls
echo ======================================================================
echo             RESTAURADOR DE BACKUPS DO ANTIGRAVITY
echo ======================================================================
echo.

set PYTHON_CMD=
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    goto executar
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    goto executar
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto executar
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto executar
)

if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python313\python.exe"
    goto executar
)

if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python312\python.exe"
    goto executar
)

echo [!] Python nao foi encontrado no sistema.
pause
exit /b 1

:executar
"%PYTHON_CMD%" "%~dp0restaurar.py"
echo.
pause
