# -*- coding: utf-8 -*-
"""
================================================================================
  SISTEMA DE BACKUP E SINCRONIZAÇÃO INTELIGENTE DO ANTIGRAVITY
================================================================================
Desenvolvido para preservar:
1. Conversas e chats em formato Markdown legível e com histórico completo.
2. Dados brutos do Antigravity (SQLite .db e transcript.jsonl) para restauração total.
3. Projetos de desenvolvimento em pastas sincronizadas e compactados em .zip.
4. Repositórios Git locais e remotos (GitHub), incluindo pacotes .bundle portáteis.
5. Sincronização automática para OneDrive e/ou Google Drive (ou destino local).
================================================================================
"""

import os
import sys
import json
import sqlite3
import shutil
import zipfile
import re
import stat
import string
import subprocess
import urllib.request
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def get_default_antigravity_dir():
    return os.environ.get("ANTIGRAVITY_DATA_DIR") or os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")

DEFAULT_CONFIG = {
    "antigravity_dir": get_default_antigravity_dir(),
    "projects": [],
    "github_users": [],
    "git_local_repos": [],
    "custom_destinations": [],
    "create_zip_archives": True,
    "copy_project_folders": True,
    "export_chat_markdown": True,
    "export_chat_raw": True,
    "backup_git_bundles": True
}

ANTIGRAVITY_EXPLANATION = """# 🛡️ Instruções do Sistema de Backup do Antigravity

> **Atenção para qualquer instância ou usuário do Antigravity:**
> Esta pasta (`Antigravity_Backups`) é o repositório centralizado de sincronização e backup em nuvem.

---

## 📌 Função Deste Sistema
1. **Preservação de Conversas e Histórico:**
   - Todo chat do Antigravity é exportado em formato Markdown legível em `Chats/Markdown/`.
   - Os dados originais (banco SQLite `.db` e `transcript.jsonl`) ficam armazenados em `Chats/Raw_Data/`.
   - O arquivo `Chats/INDEX.md` mantém o catálogo ordenado de todas as sessões.

2. **Preservação de Projetos de Desenvolvimento:**
   - Os projetos ativos são mantidos na pasta `Projetos/` (cópia estruturada e arquivos `.zip` em `Projetos/_Zips/`).

3. **Preservação Completa de Repositórios Git:**
   - Todos os repositórios Git (locais e remotos) são mantidos em `Projetos_Git/`.
   - Inclui árvores clonadas, pacotes portáteis `.bundle` (com 100% dos commits, tags e branches) e arquivos compactados `.zip`.

4. **Sincronização Dupla Inteligente (OneDrive & Google Drive):**
   - O sistema detecta automaticamente se o **OneDrive** e o **Google Drive** estão presentes.
   - Quando o Google Drive está ativo, ele salva **obrigatoriamente em AMBOS** (OneDrive e Google Drive simultaneamente).
   - Se o Google Drive não estiver ativo, salva no OneDrive (ou pasta local de emergência) e monitora a ativação.

---

## 🚀 Como Acionar a Sincronização
Para executar a sincronização a qualquer momento:
- Dê dois cliques em `Sincronizar_Drive.bat`
- Ou execute no terminal:
```powershell
python sync_to_drive.py
```

## 📂 Estrutura do Backup
```text
Antigravity_Backups/
├── Chats/
│   ├── Markdown/       <- Diálogos completos formatados em .md
│   ├── Raw_Data/       <- SQLite .db e transcript.jsonl brutos (para restauração)
│   └── INDEX.md        <- Tabela interativa com índice de todos os chats
├── Projetos/
│   ├── [NomeProjeto]/  <- Cópia sincronizada dos arquivos de trabalho
│   └── _Zips/          <- Arquivos .zip compactados para download rápido
├── Projetos_Git/
│   ├── Repositorios/   <- Clones locais dos repositórios GitHub
│   ├── Git_Bundles/    <- Arquivos .bundle autônomos (histórico completo de commits)
│   └── _Zips/          <- Zips dos repositórios Git
├── INSTRUCOES_ANTIGRAVITY.md <- Este documento explicativo
└── ULTIMO_BACKUP.txt   <- Log e data da última execução bem-sucedida
```
"""

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
                cfg = json.load(f)
                res = {**DEFAULT_CONFIG, **cfg}
                if not res.get("antigravity_dir"):
                    res["antigravity_dir"] = get_default_antigravity_dir()
                return res
        except Exception as e:
            print(f"[!] Erro ao carregar config.json: {e}. Usando configuração padrão.")
    else:
        # Save a clean template
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
            print("[i] Arquivo config.json padrão gerado com sucesso.")
        except Exception:
            pass
    return DEFAULT_CONFIG

def clean_title(title):
    if not title:
        return "Conversa Antigravity"
    replacements = {
        "o": "ão",
        "Vdeos": "Vídeos",
        "Extenso": "Extensão",
        "Criao": "Criação",
        "Apresentao": "Apresentação"
    }
    for k, v in replacements.items():
        title = title.replace(k, v)
    return title.strip()

def sanitize_filename(name):
    clean = clean_title(name)
    clean = re.sub(r'[\\/*?:"<>|]', '_', clean)
    clean = clean.strip().strip('.')
    return clean[:90] if len(clean) > 90 else clean

def is_valid_uuid(val):
    return bool(re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', str(val).strip()))

def safe_copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        try:
            os.chmod(dst, stat.S_IWRITE)
        except Exception:
            pass
    shutil.copy2(src, dst)

def detect_onedrive_targets():
    targets = []
    # Check environment variables first
    for env_var in ["OneDrive", "OneDriveCommercial", "OneDriveConsumer"]:
        val = os.environ.get(env_var)
        if val and os.path.exists(val):
            backup_folder = os.path.join(val, "Antigravity_Backups")
            os.makedirs(backup_folder, exist_ok=True)
            targets.append(backup_folder)

    # Check user home for standard folder names
    user_home = os.path.expanduser("~")
    for name in ["OneDrive - SENAC RIO", "OneDrive", "OneDrive - Pessoal", "OneDrive - Corporativo"]:
        path = os.path.join(user_home, name)
        if os.path.exists(path):
            backup_folder = os.path.join(path, "Antigravity_Backups")
            os.makedirs(backup_folder, exist_ok=True)
            targets.append(backup_folder)

    return list(dict.fromkeys(targets))

def detect_google_drive_targets():
    targets = []
    # Check all Windows drive letters (Google Drive desktop app mounts as G:, H:, etc.)
    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        if os.path.exists(root):
            for sub in ["Meu Drive", "My Drive"]:
                cand = os.path.join(root, sub)
                if os.path.exists(cand):
                    bpath = os.path.join(cand, "Antigravity_Backups")
                    os.makedirs(bpath, exist_ok=True)
                    targets.append(bpath)
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                vol_buf = ctypes.create_unicode_buffer(1024)
                fs_buf = ctypes.create_unicode_buffer(1024)
                if kernel32.GetVolumeInformationW(root, vol_buf, 1024, None, None, None, fs_buf, 1024):
                    if "google" in vol_buf.value.lower():
                        bpath = os.path.join(root, "Antigravity_Backups")
                        os.makedirs(bpath, exist_ok=True)
                        targets.append(bpath)
            except Exception:
                pass

    # Check user home directory
    user_home = os.path.expanduser("~")
    for name in ["Google Drive", "Meu Drive"]:
        local_p = os.path.join(user_home, name)
        if os.path.exists(local_p):
            for sub in ["Meu Drive", "My Drive"]:
                cand = os.path.join(local_p, sub)
                if os.path.exists(cand):
                    bpath = os.path.join(cand, "Antigravity_Backups")
                    os.makedirs(bpath, exist_ok=True)
                    targets.append(bpath)
            bpath = os.path.join(local_p, "Antigravity_Backups")
            os.makedirs(bpath, exist_ok=True)
            targets.append(bpath)

    return list(dict.fromkeys(targets))

def backup_git_projects(target_dir, local_repos, github_users, do_bundle=True, do_zip=True):
    git_dir = os.path.join(target_dir, "Projetos_Git")
    repos_dir = os.path.join(git_dir, "Repositorios")
    bundles_dir = os.path.join(git_dir, "Git_Bundles")
    zips_dir = os.path.join(git_dir, "_Zips")
    
    os.makedirs(git_dir, exist_ok=True)
    os.makedirs(repos_dir, exist_ok=True)
    if do_bundle:
        os.makedirs(bundles_dir, exist_ok=True)
    if do_zip:
        os.makedirs(zips_dir, exist_ok=True)

    backed_repos = []
    
    # 1. Backup GitHub Repositories for specified users
    for gh_user in github_users:
        if not gh_user or not gh_user.strip():
            continue
        gh_user = gh_user.strip()
        print(f"[+] Verificando repositórios do GitHub para o usuário: {gh_user}...")
        try:
            url = f"https://api.github.com/users/{gh_user}/repos"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                repos_data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[!] Não foi possível listar repositórios do GitHub para {gh_user}: {e}")
            repos_data = []

        for repo in repos_data:
            rname = repo.get("name")
            clone_url = repo.get("clone_url")
            if not rname or not clone_url:
                continue
                
            dest_repo = os.path.join(repos_dir, rname)
            print(f"  -> Sincronizando repositório Git: {gh_user}/{rname}...")
            
            # Clone or pull
            if os.path.exists(dest_repo) and os.path.exists(os.path.join(dest_repo, ".git")):
                try:
                    subprocess.run(["git", "-C", dest_repo, "pull"], capture_output=True, timeout=30)
                except Exception as e:
                    print(f"     [!] Erro ao atualizar repo {rname}: {e}")
            else:
                try:
                    subprocess.run(["git", "clone", clone_url, dest_repo], capture_output=True, timeout=60)
                except Exception as e:
                    print(f"     [!] Erro ao clonar repo {rname}: {e}")

            # Create Git Bundle (100% offline portable repo with full history)
            if do_bundle and os.path.exists(dest_repo) and os.path.exists(os.path.join(dest_repo, ".git")):
                try:
                    b_file = os.path.join(bundles_dir, f"{rname}.bundle")
                    subprocess.run(["git", "-C", dest_repo, "bundle", "create", b_file, "--all"], capture_output=True, timeout=30)
                except Exception as e:
                    print(f"     [!] Erro ao criar bundle para {rname}: {e}")

            # Create ZIP
            if do_zip and os.path.exists(dest_repo):
                try:
                    z_file = os.path.join(zips_dir, f"{rname}.zip")
                    with zipfile.ZipFile(z_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(dest_repo):
                            dirs[:] = [d for d in dirs if d not in ["node_modules", ".gradle", "__pycache__", ".venv", "venv"]]
                            for file in files:
                                full_p = os.path.join(root, file)
                                rel_p = os.path.relpath(full_p, dest_repo)
                                zipf.write(full_p, arcname=os.path.join(rname, rel_p))
                except Exception as e:
                    print(f"     [!] Erro ao criar zip para {rname}: {e}")
                    
            backed_repos.append(rname)

    # 2. Backup Local Git Repos
    for loc_r in local_repos:
        if not loc_r or not os.path.exists(loc_r) or not os.path.exists(os.path.join(loc_r, ".git")):
            continue
        lrname = os.path.basename(loc_r.rstrip(r"\/"))
        if lrname not in backed_repos:
            print(f"  -> Gerando pacote Git para repo local: {lrname}...")
            if do_bundle:
                try:
                    b_file = os.path.join(bundles_dir, f"{lrname}.bundle")
                    subprocess.run(["git", "-C", loc_r, "bundle", "create", b_file, "--all"], capture_output=True, timeout=30)
                    backed_repos.append(lrname)
                except Exception as e:
                    print(f"     [!] Erro ao criar bundle para {lrname}: {e}")

            if do_zip:
                try:
                    z_file = os.path.join(zips_dir, f"{lrname}.zip")
                    with zipfile.ZipFile(z_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(loc_r):
                            dirs[:] = [d for d in dirs if d not in ["node_modules", ".gradle", "__pycache__", ".venv", "venv"]]
                            for file in files:
                                full_p = os.path.join(root, file)
                                rel_p = os.path.relpath(full_p, loc_r)
                                zipf.write(full_p, arcname=os.path.join(lrname, rel_p))
                except Exception as e:
                    print(f"     [!] Erro ao criar zip para {lrname}: {e}")

    return list(dict.fromkeys(backed_repos))

def get_conversations_metadata(antigravity_dir):
    db_path = os.path.join(antigravity_dir, "conversation_summaries.db")
    convs = {}
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT conversation_id, title, step_count, last_modified_time, workspace_uris, status 
                FROM conversation_summaries
            """)
            for row in cur.fetchall():
                cid, title, steps, mod_time, ws_uris, status = row
                if not is_valid_uuid(cid):
                    continue
                convs[cid] = {
                    "conversation_id": cid,
                    "title": clean_title(title) if title else f"Conversa {cid[:8]}",
                    "step_count": steps or 0,
                    "last_modified": mod_time or "",
                    "workspaces": ws_uris or "[]",
                    "status": status or ""
                }
            conn.close()
        except Exception as e:
            print(f"[!] Erro ao ler conversation_summaries.db: {e}")
    
    brain_dir = os.path.join(antigravity_dir, "brain")
    if os.path.exists(brain_dir):
        for cid in os.listdir(brain_dir):
            if is_valid_uuid(cid) and cid not in convs:
                convs[cid] = {
                    "conversation_id": cid,
                    "title": f"Conversa {cid[:8]}",
                    "step_count": 0,
                    "last_modified": "",
                    "workspaces": "[]",
                    "status": "DESCONHECIDO"
                }
    return convs

def convert_transcript_to_markdown(transcript_path, metadata):
    title = clean_title(metadata.get("title", "Conversa Antigravity"))
    cid = metadata.get("conversation_id", "")
    last_mod = metadata.get("last_modified", "")
    workspaces = metadata.get("workspaces", "")
    
    lines = [
        f"# {title}",
        "",
        f"- **ID da Conversa:** `{cid}`",
        f"- **Última Modificação:** {last_mod}",
        f"- **Workspaces:** `{workspaces}`",
        f"- **Data do Backup:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        ""
    ]
    
    if not os.path.exists(transcript_path):
        lines.append("*Arquivo de transcrição não encontrado.*")
        return "\n".join(lines)
    
    with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                entry = json.loads(raw_line)
            except Exception:
                continue
            
            stype = entry.get("type", "")
            time_str = entry.get("created_at", "")
            content = entry.get("content", "")
            tool_calls = entry.get("tool_calls", [])
            
            if stype == "USER_INPUT":
                user_msg = content or ""
                if "<USER_REQUEST>" in user_msg:
                    match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", user_msg, re.DOTALL)
                    if match:
                        user_msg = match.group(1).strip()
                lines.append(f"## 👤 Usuário ({time_str})\n")
                lines.append(user_msg)
                lines.append("\n---\n")
                
            elif stype == "PLANNER_RESPONSE":
                agent_sections = []
                if content and content.strip():
                    agent_sections.append(content.strip())
                
                if tool_calls:
                    tool_items = []
                    for tc in tool_calls:
                        func = tc.get("function", {})
                        fname = func.get("name", "ferramenta")
                        fargs = func.get("arguments", {})
                        if isinstance(fargs, str):
                            try:
                                fargs = json.loads(fargs)
                            except Exception:
                                pass
                        summary = fargs.get("toolSummary", "") if isinstance(fargs, dict) else ""
                        if summary:
                            tool_items.append(f"- **{fname}**: {summary}")
                        else:
                            tool_items.append(f"- **{fname}**")
                    if tool_items:
                        agent_sections.append("<details><summary>🛠️ <i>Ações e Ferramentas Executadas</i></summary>\n\n" + "\n".join(tool_items) + "\n</details>")
                
                if agent_sections:
                    lines.append("## 🤖 Assistente Antigravity\n")
                    lines.append("\n\n".join(agent_sections))
                    lines.append("\n---\n")

    return "\n".join(lines)

def backup_projects(projects, target_dir, do_copy=True, do_zip=True):
    proj_dir = os.path.join(target_dir, "Projetos")
    os.makedirs(proj_dir, exist_ok=True)
    zip_dir = os.path.join(proj_dir, "_Zips")
    if do_zip:
        os.makedirs(zip_dir, exist_ok=True)
        
    backed_up = []
    
    for p in projects:
        if not p or not os.path.exists(p):
            if p:
                print(f"[-] Projeto não encontrado (ignorado): {p}")
            continue
        
        pname = os.path.basename(p.rstrip(r"\/"))
        dest_folder = os.path.join(proj_dir, pname)
        
        print(f"[+] Fazendo backup do projeto: {pname}...")
        
        if do_copy:
            try:
                def ignore_patterns(folder, names):
                    ignored = set()
                    for n in names:
                        if n in ["node_modules", ".gradle", "__pycache__", ".pytest_cache", ".venv", "venv", "dist", "build"]:
                            ignored.add(n)
                    return ignored
                
                shutil.copytree(p, dest_folder, dirs_exist_ok=True, copy_function=safe_copy, ignore=ignore_patterns)
            except Exception as e:
                print(f"[!] Erro ao copiar pasta do projeto {pname}: {e}")
        
        if do_zip:
            try:
                zip_path = os.path.join(zip_dir, f"{pname}.zip")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(p):
                        dirs[:] = [d for d in dirs if d not in ["node_modules", ".gradle", "__pycache__", ".pytest_cache", ".venv", "venv", "dist", "build"]]
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, p)
                            zipf.write(full_path, arcname=os.path.join(pname, rel_path))
            except Exception as e:
                print(f"[!] Erro ao criar ZIP do projeto {pname}: {e}")
                
        backed_up.append(pname)
    return backed_up

def backup_chats(antigravity_dir, target_dir, convs_meta, export_md=True, export_raw=True):
    chats_dir = os.path.join(target_dir, "Chats")
    md_dir = os.path.join(chats_dir, "Markdown")
    raw_dir = os.path.join(chats_dir, "Raw_Data")
    
    if export_md:
        os.makedirs(md_dir, exist_ok=True)
    if export_raw:
        os.makedirs(raw_dir, exist_ok=True)
        
    brain_dir = os.path.join(antigravity_dir, "brain")
    conv_db_dir = os.path.join(antigravity_dir, "conversations")
    
    index_rows = []
    
    print("[+] Processando histórico de chats...")
    for cid, meta in convs_meta.items():
        if not is_valid_uuid(cid):
            continue
        title = clean_title(meta.get("title", "Conversa"))
        safe_title = sanitize_filename(title)
        md_filename = f"{safe_title}_{cid[:8]}.md"
        
        transcript_path = os.path.join(brain_dir, cid, ".system_generated", "logs", "transcript.jsonl")
        
        if export_md:
            try:
                md_content = convert_transcript_to_markdown(transcript_path, meta)
                md_dest = os.path.join(md_dir, md_filename)
                with open(md_dest, "w", encoding="utf-8") as f:
                    f.write(md_content)
            except Exception as e:
                print(f"[!] Erro ao gerar Markdown para chat {title}: {e}")
        
        if export_raw:
            try:
                dest_conv_raw = os.path.join(raw_dir, cid)
                os.makedirs(dest_conv_raw, exist_ok=True)
                if os.path.exists(transcript_path):
                    safe_copy(transcript_path, os.path.join(dest_conv_raw, "transcript.jsonl"))
                
                sqlite_file = os.path.join(conv_db_dir, f"{cid}.db")
                if os.path.exists(sqlite_file):
                    safe_copy(sqlite_file, os.path.join(dest_conv_raw, f"{cid}.db"))
            except Exception as e:
                print(f"[!] Erro ao copiar dados brutos do chat {cid}: {e}")
                
        index_rows.append({
            "title": title,
            "cid": cid,
            "md_file": f"Markdown/{md_filename}",
            "steps": meta.get("step_count", 0),
            "last_modified": meta.get("last_modified", "")
        })
        
    sum_db = os.path.join(antigravity_dir, "conversation_summaries.db")
    if os.path.exists(sum_db) and export_raw:
        safe_copy(sum_db, os.path.join(raw_dir, "conversation_summaries.db"))
        
    index_md_path = os.path.join(chats_dir, "INDEX.md")
    index_lines = [
        "# 📑 Índice de Conversas e Chats do Antigravity",
        "",
        f"> Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Título do Chat | Passos | Última Modificação | Arquivo Markdown | ID |",
        "|---|---|---|---|---|"
    ]
    for r in sorted(index_rows, key=lambda x: str(x["last_modified"]), reverse=True):
        index_lines.append(f"| **{r['title']}** | {r['steps']} | {r['last_modified'][:19] if r['last_modified'] else '-'} | [{r['md_file']}]({r['md_file']}) | `{r['cid'][:8]}` |")
        
    index_lines.append("")
    with open(index_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))
        
    print(f"[✔] {len(index_rows)} chats processados e salvos com sucesso!")
    return len(index_rows)

def write_antigravity_instructions(target_dir):
    readme_path = os.path.join(target_dir, "INSTRUCOES_ANTIGRAVITY.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(ANTIGRAVITY_EXPLANATION)

def main():
    print("==================================================")
    print("   SISTEMA DE BACKUP ANTIGRAVITY -> NUVEM/DRIVE   ")
    print("==================================================")
    
    cfg = load_config()
    projects = cfg.get("projects", [])
    local_git_repos = cfg.get("git_local_repos", [])
    github_users = cfg.get("github_users", [])
    antigravity_dir = cfg.get("antigravity_dir") or get_default_antigravity_dir()
    custom_dests = cfg.get("custom_destinations", [])
    
    if not os.path.exists(antigravity_dir):
        print(f"[!] ATENÇÃO: Diretório do Antigravity não encontrado em: {antigravity_dir}")
        print("    Verifique o caminho no arquivo config.json.")
    else:
        print(f"[+] Antigravity detectado em: {antigravity_dir}")
        
    onedrive_targets = detect_onedrive_targets()
    print(f"\n[1] Verificação do OneDrive:")
    if onedrive_targets:
        for t in onedrive_targets:
            print(f"    [✔] Ativo: {t}")
    else:
        print("    [-] Nenhum OneDrive encontrado no sistema.")

    gdrive_targets = detect_google_drive_targets()
    print(f"\n[2] Verificação do Google Drive:")
    if gdrive_targets:
        for t in gdrive_targets:
            print(f"    [✔] Google Drive detectado e ativo: {t}")
    else:
        print("    [-] Google Drive NÃO detectado no momento.")
        if onedrive_targets:
            print("    [i] O backup será salvo no OneDrive e, assim que o Google Drive for conectado,")
            print("        o sistema salvará automaticamente em AMBOS (OneDrive + Google Drive)!")

    # Custom destinations
    custom_active = []
    if custom_dests:
        print(f"\n[3] Verificação de Destinos Personalizados:")
        for cd in custom_dests:
            if os.path.exists(cd):
                bpath = os.path.join(cd, "Antigravity_Backups")
                os.makedirs(bpath, exist_ok=True)
                custom_active.append(bpath)
                print(f"    [✔] Destino personalizado ativo: {bpath}")
            else:
                print(f"    [-] Destino não encontrado: {cd}")

    active_targets = list(dict.fromkeys(onedrive_targets + gdrive_targets + custom_active))
    
    if not active_targets:
        fallback = os.path.join(os.path.expanduser("~"), "Antigravity_Backups")
        os.makedirs(fallback, exist_ok=True)
        active_targets.append(fallback)
        print(f"\n[!] Nenhum drive de nuvem detectado. Usando destino local de emergência:")
        print(f"    -> {fallback}")
        
    convs_meta = get_conversations_metadata(antigravity_dir)
    print(f"\n[i] Total de conversas encontradas no Antigravity: {len(convs_meta)}")
    
    for target in active_targets:
        is_gdrive = "google" in target.lower() or (len(target) >= 2 and target[1] == ':' and target[0].upper() not in ['C'])
        dest_type = "Google Drive" if is_gdrive else ("OneDrive" if "onedrive" in target.lower() else "Local/Externo")
        
        print(f"\n---> Sincronizando para [{dest_type}]: {target}")
        
        # 1. Backup Standard Projects
        backed_projects = backup_projects(
            projects, 
            target, 
            do_copy=cfg.get("copy_project_folders", True),
            do_zip=cfg.get("create_zip_archives", True)
        )
        
        # 2. Backup Git Repositories (GitHub + Local Bundles)
        backed_git = backup_git_projects(
            target,
            local_git_repos,
            github_users,
            do_bundle=cfg.get("backup_git_bundles", True),
            do_zip=cfg.get("create_zip_archives", True)
        )
        
        # 3. Backup Chats
        chat_count = backup_chats(
            antigravity_dir,
            target,
            convs_meta,
            export_md=cfg.get("export_chat_markdown", True),
            export_raw=cfg.get("export_chat_raw", True)
        )
        
        write_antigravity_instructions(target)
        
        log_file = os.path.join(target, "ULTIMO_BACKUP.txt")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Último backup realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Destino: {dest_type} ({target})\n")
            f.write(f"Projetos salvos: {', '.join(backed_projects) if backed_projects else 'Nenhum projeto configurado'}\n")
            f.write(f"Repositórios Git salvos: {', '.join(backed_git) if backed_git else 'Nenhum repositório configurado'}\n")
            f.write(f"Total de chats salvos: {chat_count}\n")
            f.write("Status: Sincronização concluída com sucesso!\n")
            
    print("\n==================================================")
    print("   ✔ BACKUP E SINCRONIZAÇÃO FINALIZADOS COM SUCESSO! ")
    print("==================================================")

if __name__ == "__main__":
    main()
