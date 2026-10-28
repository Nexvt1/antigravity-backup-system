# -*- coding: utf-8 -*-
"""
Assistente de Configuração e Instalação do Sistema de Backup do Antigravity
Configura automaticamente os caminhos para o usuário atual no Windows.
"""

import os
import sys
import json
import subprocess
import shutil

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
CONFIG_EXAMPLE_PATH = os.path.join(BASE_DIR, "config.example.json")

def find_antigravity_dir():
    candidates = [
        os.path.join(os.path.expanduser("~"), ".gemini", "antigravity"),
        os.environ.get("ANTIGRAVITY_DATA_DIR", "")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")

def scan_for_git_repos():
    user_dir = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_dir, "Documents"),
        os.path.join(user_dir, "Desktop"),
        os.path.join(user_dir, "Downloads"),
        os.path.join(user_dir, "Projetos"),
        os.path.join(user_dir, "Projects")
    ]
    
    found = []
    print("[*] Procurando repositórios Git em suas pastas (Documentos, Downloads, Desktop)...")
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        try:
            for root, dirs, files in os.walk(sdir):
                # Ignorar pastas muito pesadas ou internas
                skip_list = ["AppData", ".vscode", "node_modules", ".gradle", "site-packages", ".gemini", "venv", ".venv", "dist", "build"]
                if any(skip in root for skip in skip_list):
                    dirs[:] = []
                    continue
                if ".git" in dirs:
                    found.append(root)
                    dirs.remove(".git")
        except Exception:
            pass
    return sorted(list(dict.fromkeys(found)))

def create_desktop_shortcut():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop):
        return None
    
    bat_content = f"""@echo off
title Sincronizacao Antigravity
chcp 65001 > nul
cls
echo ==================================================
echo    SINCRONIZANDO CHATS E PROJETOS ANTIGRAVITY
echo ==================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "{os.path.join(BASE_DIR, 'sync_to_drive.py')}"
    goto fim
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py "{os.path.join(BASE_DIR, 'sync_to_drive.py')}"
    goto fim
)

echo [!] Python nao foi encontrado no PATH do sistema.
echo Por favor, instale o Python ou execute sync_to_drive.py manualmente.
pause
exit /b 1

:fim
echo.
echo Processo concluido!
pause
"""
    dest_path = os.path.join(desktop, "Sincronizar_Antigravity.bat")
    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        return dest_path
    except Exception as e:
        print(f"[!] Erro ao criar atalho no Desktop: {e}")
        return None

def main():
    print("=" * 60)
    print("  INSTALADOR E CONFIGURADOR DO BACKUP ANTIGRAVITY  ")
    print("=" * 60)
    print("\nEste assistente irá preparar seu computador para salvar")
    print("automaticamente todas as suas conversas e projetos.\n")
    
    # 1. Antigravity dir
    ag_dir = find_antigravity_dir()
    print(f"[+] Diretório do Antigravity detectado:")
    print(f"    {ag_dir}")
    if os.path.exists(ag_dir):
        print("    -> Confirmado! Diretório existe no seu sistema.")
    else:
        print("    -> Diretório padrão preparado. Será monitorado assim que o Antigravity iniciar.")

    # 2. Git repos
    repos = scan_for_git_repos()
    if repos:
        print(f"\n[+] Encontramos {len(repos)} repositório(s) Git no seu computador:")
        for r in repos[:10]:
            print(f"    - {r}")
        if len(repos) > 10:
            print(f"    ... e mais {len(repos) - 10} repositórios.")
    else:
        print("\n[-] Nenhum repositório Git local detectado nas pastas comuns.")

    # 3. Create config.json
    cfg = {
        "antigravity_dir": ag_dir,
        "projects": repos[:8] if repos else [],
        "github_users": [],
        "git_local_repos": repos[:8] if repos else [],
        "custom_destinations": [],
        "create_zip_archives": True,
        "copy_project_folders": True,
        "export_chat_markdown": True,
        "export_chat_raw": True,
        "backup_git_bundles": True
    }
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        
    print(f"\n[✔] Arquivo 'config.json' gerado e personalizado com sucesso!")
    print(f"    Você pode editá-lo a qualquer momento com o Bloco de Notas para")
    print(f"    adicionar seu usuário do GitHub ou novas pastas de projetos.")

    # 4. Create Desktop Shortcut
    sc = create_desktop_shortcut()
    if sc:
        print(f"\n[✔] Atalho de 1 clique criado na sua Área de Trabalho:")
        print(f"    -> {sc}")

    print("\n" + "=" * 60)
    print("  INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("Para iniciar o seu primeiro backup, dê dois cliques no ícone")
    print("'Sincronizar_Antigravity' na sua Área de Trabalho ou execute:")
    print("    python sync_to_drive.py\n")

if __name__ == "__main__":
    main()
