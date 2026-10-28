# 🛡️ Sistema de Backup e Sincronização Inteligente do Antigravity

Um sistema completo, automatizado e portátil para proteger e sincronizar todas as suas conversas, sessões da IA, bancos de dados e projetos de desenvolvimento do **Google Antigravity** na nuvem (**OneDrive** e **Google Drive**) ou em armazenamento local.

---

## ✨ Principais Funcionalidades

### 1. 💬 Conversas em Markdown Legível
- Exporta todas as sessões e chats do Antigravity em formato `.md` de alta legibilidade.
- Inclui mensagens do usuário, respostas do assistente e ferramentas executadas detalhadas em abas retráteis.
- Gera automaticamente o arquivo `Chats/INDEX.md` com um índice interativo de todas as conversas ordenadas por data e número de passos.

### 2. 💾 Preservação de Dados Brutos (Full Restore)
- Salva os arquivos originais `transcript.jsonl` e bancos SQLite (`.db`).
- Inclui o script `Restaurar_Backup.bat` para recuperar todo o histórico do Antigravity em um novo computador ou após formatação em poucos segundos.

### 3. 📂 Backup Inteligente de Projetos
- Copia suas pastas de trabalho ignorando automaticamente pastas pesadas de cache (`node_modules`, `.gradle`, `venv`, `__pycache__`, etc.).
- Compacta cada projeto em arquivos `.zip` independentes na pasta `Projetos/_Zips/` para fácil compartilhamento e download.

### 4. 🐙 Preservação Total de Repositórios Git
- **GitHub Remoto**: Conecta-se à API do GitHub e clona/atualiza automaticamente todos os repositórios dos usuários configurados.
- **Git Bundles (.bundle)**: Gera arquivos `.bundle` autônomos que guardam 100% dos commits, branches e tags de cada projeto para recuperação completa offline.
- **Zips de Repositórios**: Gera compactações `.zip` dos repositórios.

### 5. ☁️ Sincronização Dupla em Nuvem (OneDrive + Google Drive)
- **Detecção Automática**: Identifica sozinho o seu OneDrive (pessoal, corporativo ou educacional) e o Google Drive (unidades montadas `G:`, `H:`, pastas locais ou qualquer letra do Windows).
- **Salvamento Simultâneo**: Quando ambos estão conectados, salva obrigatoriamente nos dois destinos.
- **Destino Local de Emergência**: Se nenhuma nuvem estiver conectada, salva na pasta `~/Antigravity_Backups` para você nunca perder nada.

---

## 🚀 Como Instalar e Usar (Em 3 Passos)

### Passo 1: Extrair o Arquivo
Extraia o arquivo `Sistema_Backup_Antigravity.zip` para qualquer pasta de sua preferência (ex: em `Documentos` ou `C:\Users\SEU_USUARIO\backup_antigravity`).

### Passo 2: Executar o Instalador
Dê dois cliques no arquivo:
```text
instalar.bat
```
O assistente irá:
1. Verificar se o Python está presente no seu sistema.
2. Localizar automaticamente a sua pasta de dados do Antigravity.
3. Rastrear os repositórios Git existentes no seu computador para inclusão automática.
4. Gerar o seu arquivo `config.json` personalizado.
5. Criar o atalho **`Sincronizar_Antigravity.bat`** diretamente na sua **Área de Trabalho**.

### Passo 3: Sincronizar Sempre que Quiser
Basta dar dois cliques no ícone na sua **Área de Trabalho** ou executar:
```text
Sincronizar_Drive.bat
```

---

## ⚙️ Personalização (`config.json`)

Você pode abrir o arquivo `config.json` com o Bloco de Notas para personalizar suas opções:

```json
{
  "antigravity_dir": "",
  "projects": [
    "C:\\Users\\SEU_NOME\\Documents\\MeuProjeto1",
    "C:\\Users\\SEU_NOME\\Downloads\\MeuProjeto2"
  ],
  "github_users": [
    "seu_usuario_github"
  ],
  "git_local_repos": [
    "C:\\Users\\SEU_NOME\\Documents\\MeuProjeto1"
  ],
  "custom_destinations": [
    "D:\\MeusBackups"
  ],
  "create_zip_archives": true,
  "copy_project_folders": true,
  "export_chat_markdown": true,
  "export_chat_raw": true,
  "backup_git_bundles": true
}
```

- **`antigravity_dir`**: Deixe vazio `""` para que o sistema use o caminho padrão automático (`~/.gemini/antigravity`).
- **`projects`**: Lista de pastas de projetos comuns que você quer salvar.
- **`github_users`**: Usuários do GitHub para clonar/atualizar todos os repositórios públicos automaticamente.
- **`git_local_repos`**: Repositórios Git locais para gerar pacotes `.bundle`.
- **`custom_destinations`**: Caso queira salvar em um HD externo ou pendrive além do OneDrive/Google Drive.
- **Opções booleanas (`true`/`false`)**: Ative ou desative a criação de zips, cópia de pastas, exportação de markdown, etc.

---

## 🔄 Como Restaurar um Backup

Se você formatou o computador ou comprou uma máquina nova:
1. Instale o Antigravity e o Python normalmente.
2. Dê dois cliques em:
```text
Restaurar_Backup.bat
```
3. O script detectará seu backup na nuvem ou pedirá o caminho da pasta `Antigravity_Backups`.
4. Todos os seus diálogos, resumos e conversas serão reintegrados ao Antigravity imediatamente!

---

## 📋 Estrutura Gerada no seu Drive/Nuvem

```text
Antigravity_Backups/
├── Chats/
│   ├── Markdown/               <- Todos os chats formatados em .md
│   │   ├── MinhaConversa_abc123.md
│   │   └── ...
│   ├── Raw_Data/               <- Dados originais para restauração
│   │   ├── conversation_summaries.db
│   │   └── [ID_Conversa]/
│   │       ├── transcript.jsonl
│   │       └── [ID_Conversa].db
│   └── INDEX.md                <- Tabela com links para todos os chats
├── Projetos/
│   ├── [NomeProjeto]/          <- Cópia limpa dos arquivos
│   └── _Zips/                  <- Arquivo .zip pronto para download
├── Projetos_Git/
│   ├── Repositorios/           <- Clones locais dos repositórios GitHub
│   ├── Git_Bundles/            <- Arquivos .bundle autônomos (histórico completo)
│   └── _Zips/                  <- Arquivos .zip dos repositórios Git
├── INSTRUCOES_ANTIGRAVITY.md   <- Instruções embutidas no backup
└── ULTIMO_BACKUP.txt           <- Data, hora e relatório da última sincronização
```

---

## 💻 Requisitos
- **Sistema Operacional**: Windows 10 ou Windows 11.
- **Python**: Versão 3.8 ou superior (marcar "Add Python to PATH" durante a instalação).
- **Git** (Opcional, mas recomendado): Para geração de `.bundle` e sincronização de repositórios do GitHub.
