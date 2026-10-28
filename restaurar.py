# -*- coding: utf-8 -*-
"""
Assistente de Restauração de Backups do Antigravity
Restaura chats, conversas e bancos de dados para uma nova instalação.
"""

import os
import sys
import shutil
import stat

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def find_backup_folder():
    user_home = os.path.expanduser("~")
    candidates = []
    
    # 1. Checar OneDrive
    for name in ["OneDrive - SENAC RIO", "OneDrive", "OneDrive - Pessoal"]:
        p = os.path.join(user_home, name, "Antigravity_Backups")
        if os.path.exists(p):
            candidates.append(p)
            
    # 2. Checar Google Drive e drives montados
    import string
    for letter in string.ascii_uppercase:
        p = f"{letter}:\\Meu Drive\\Antigravity_Backups"
        if os.path.exists(p):
            candidates.append(p)
        p2 = f"{letter}:\\My Drive\\Antigravity_Backups"
        if os.path.exists(p2):
            candidates.append(p2)
        p3 = f"{letter}:\\Antigravity_Backups"
        if os.path.exists(p3):
            candidates.append(p3)
            
    # 3. Checar Pasta do Usuario
    fallback = os.path.join(user_home, "Antigravity_Backups")
    if os.path.exists(fallback):
        candidates.append(fallback)
        
    return list(dict.fromkeys(candidates))

def safe_copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        try:
            os.chmod(dst, stat.S_IWRITE)
        except Exception:
            pass
    shutil.copy2(src, dst)

def main():
    print("=" * 60)
    print("      RESTAURADOR DE BACKUPS DO ANTIGRAVITY")
    print("=" * 60)
    
    backups = find_backup_folder()
    backup_path = ""
    
    if backups:
        print("\nBackups encontrados no seu computador:")
        for idx, b in enumerate(backups, 1):
            print(f"  [{idx}] {b}")
        print("\nEscolha o número do backup desejado ou digite o caminho completo:")
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(backups):
            backup_path = backups[int(choice) - 1]
        elif os.path.exists(choice):
            backup_path = choice
    else:
        print("\nNenhum backup foi detectado automaticamente nas pastas padrão.")
        print("Digite o caminho completo da pasta 'Antigravity_Backups':")
        choice = input("> ").strip()
        if os.path.exists(choice):
            backup_path = choice
            
    if not backup_path or not os.path.exists(backup_path):
        print("[!] Caminho de backup inválido. Operação cancelada.")
        return

    antigravity_dir = os.environ.get("ANTIGRAVITY_DATA_DIR") or os.path.join(os.path.expanduser("~"), ".gemini", "antigravity")
    raw_data_dir = os.path.join(backup_path, "Chats", "Raw_Data")
    
    if not os.path.exists(raw_data_dir):
        print(f"[!] Pasta Chats/Raw_Data não encontrada em: {backup_path}")
        return

    print(f"\n[+] Destino da restauração: {antigravity_dir}")
    print("[!] ATENÇÃO: Essa operação copiará o histórico e bancos de dados salvos.")
    conf = input("Deseja continuar? (S/N): ").strip().upper()
    if conf != "S":
        print("Operação cancelada.")
        return

    os.makedirs(antigravity_dir, exist_ok=True)
    
    # 1. Restaurar conversation_summaries.db se existir
    sum_db = os.path.join(raw_data_dir, "conversation_summaries.db")
    if os.path.exists(sum_db):
        dst_db = os.path.join(antigravity_dir, "conversation_summaries.db")
        safe_copy(sum_db, dst_db)
        print("[✔] Banco mestre conversation_summaries.db restaurado com sucesso!")

    # 2. Restaurar conversas individuais
    restored_count = 0
    conv_target_dir = os.path.join(antigravity_dir, "conversations")
    brain_target_dir = os.path.join(antigravity_dir, "brain")
    
    for item in os.listdir(raw_data_dir):
        item_path = os.path.join(raw_data_dir, item)
        if os.path.isdir(item_path):
            cid = item
            # Restaurar transcript.jsonl
            src_transcript = os.path.join(item_path, "transcript.jsonl")
            if os.path.exists(src_transcript):
                dst_transcript = os.path.join(brain_target_dir, cid, ".system_generated", "logs", "transcript.jsonl")
                safe_copy(src_transcript, dst_transcript)
                
            # Restaurar .db da conversa
            src_conv_db = os.path.join(item_path, f"{cid}.db")
            if os.path.exists(src_conv_db):
                dst_conv_db = os.path.join(conv_target_dir, f"{cid}.db")
                safe_copy(src_conv_db, dst_conv_db)
                
            restored_count += 1

    print(f"\n[✔] Restauração concluída! {restored_count} conversa(s) restaurada(s).")
    print("Abra o Antigravity para visualizar seu histórico recuperado.\n")

if __name__ == "__main__":
    main()
