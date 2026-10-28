@echo off
title Sincronizacao Antigravity para Nuvem/Drive
chcp 65001 > nul
cls
echo ======================================================================
echo           SINCRONIZANDO CHATS E PROJETOS PARA A NUVEM
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
echo Instale o Python ou adicione-o ao PATH do Windows.
pause
exit /b 1

:executar
"%PYTHON_CMD%" "%~dp0sync_to_drive.py"
echo.
echo ======================================================================
echo Processo finalizado!
echo ======================================================================
pause
