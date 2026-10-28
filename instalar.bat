@echo off
title Instalador do Sistema de Backup Antigravity
chcp 65001 > nul
cls

echo ======================================================================
echo       INSTALADOR DO SISTEMA DE BACKUP E SINCRONIZACAO ANTIGRAVITY
echo ======================================================================
echo.

:: 1. Verificar se Python esta instalado
set PYTHON_CMD=
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=python
    goto check_git
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PYTHON_CMD=py
    goto check_git
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto check_git
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto check_git
)

if exist "C:\Program Files\Python313\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python313\python.exe"
    goto check_git
)

if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_CMD=C:\Program Files\Python312\python.exe"
    goto check_git
)

echo [!] ERRO: O Python nao foi encontrado no seu computador!
echo.
echo Para usar o sistema de backup, instale o Python:
echo   1. Acesse: https://www.python.org/downloads/
echo   2. Marque a opcao "Add python.exe to PATH" durante a instalacao.
echo.
pause
exit /b 1

:check_git
:: 2. Verificar se Git esta instalado (opcional para bundles)
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [i] AVISO: Git nao detectado no PATH. O backup de conversas e pastas
    echo     funcionara perfeitamente, mas os recursos de clonagem e .bundle
    echo     do Git necessitam do Git instalado: https://git-scm.com/
    echo.
)

:: 3. Executar o configurador inteligente
echo [*] Executando assistente de configuracao...
echo.
"%PYTHON_CMD%" "%~dp0configurar.py"

echo.
echo Deseja realizar o primeiro backup agora mesmo? (S/N)
set /p RESPOSTA="> "
if /i "%RESPOSTA%"=="S" (
    echo.
    echo [*] Iniciando primeiro backup...
    echo.
    "%PYTHON_CMD%" "%~dp0sync_to_drive.py"
)

echo.
echo ======================================================================
echo  Pronto! Voce ja pode usar o atalho 'Sincronizar_Antigravity' na sua
echo  Area de Trabalho sempre que quiser salvar seus chats e projetos.
echo ======================================================================
echo.
pause
