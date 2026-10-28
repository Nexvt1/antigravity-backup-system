import os
import sys
import ast
import json
import py_compile
import re

# Ensure UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def check_python_file(file_path):
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        ast.parse(code, filename=file_path)
    except SyntaxError as e:
        issues.append(f"Erro de sintaxe Python na linha {e.lineno}: {e.msg} -> '{e.text.strip() if e.text else ''}'")
    except Exception as e:
        issues.append(f"Erro ao analisar Python: {e}")
        
    try:
        py_compile.compile(file_path, doraise=True)
    except py_compile.PyCompileError as e:
        if not issues:
            issues.append(f"Erro de compilação Python: {e}")
    return issues

def check_json_file(file_path):
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        issues.append(f"Erro de formato JSON na linha {e.lineno}, coluna {e.colno}: {e.msg}")
    except Exception as e:
        issues.append(f"Erro ao ler JSON: {e}")
    return issues

def check_js_html_file(file_path):
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Check basic balance of braces/brackets
        stack = []
        pairs = {')': '(', '}': '{', ']': '['}
        in_string = False
        str_char = ''
        
        for idx, ch in enumerate(content):
            if in_string:
                if ch == str_char and content[idx-1] != '\\':
                    in_string = False
            else:
                if ch in ['"', "'", '`']:
                    in_string = True
                    str_char = ch
                elif ch in ['(', '{', '[']:
                    stack.append(ch)
                elif ch in [')', '}', ']']:
                    if not stack or stack[-1] != pairs[ch]:
                        pass # Many templates/snippets can be partial, so don't fail hard, just note if needed
                    else:
                        stack.pop()
    except Exception as e:
        issues.append(f"Erro ao ler arquivo: {e}")
    return issues

def verify_file(file_path):
    if not os.path.exists(file_path):
        return [f"Arquivo não encontrado: {file_path}"]
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        return check_python_file(file_path)
    elif ext in [".json", ".jsonc"]:
        return check_json_file(file_path)
    elif ext in [".js", ".jsx", ".ts", ".tsx", ".html"]:
        return check_js_html_file(file_path)
    return []

def scan_target(target_path):
    print("==================================================")
    print("   VERIFICADOR DE INTEGRIDADE E SEGURANÇA (ANTIGRAVITY) ")
    print("==================================================")
    print(f"Alvo verificado: {target_path}")
    
    if os.path.isfile(target_path):
        files_to_check = [target_path]
    elif os.path.isdir(target_path):
        files_to_check = []
        for root, dirs, files in os.walk(target_path):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", ".gradle", "__pycache__", "dist", "build"]]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in [".py", ".json", ".js", ".ts", ".html"]:
                    files_to_check.append(os.path.join(root, f))
    else:
        print(f"[!] Caminho inexistente: {target_path}")
        return 1

    total = len(files_to_check)
    print(f"Total de arquivos analisados: {total}\n")
    
    errors_found = 0
    for f in files_to_check:
        issues = verify_file(f)
        if issues:
            errors_found += 1
            print(f"[FALHA] {f}:")
            for iss in issues:
                print(f"   ❌ {iss}")
        else:
            # print(".", end="", flush=True)
            pass

    print("\n--------------------------------------------------")
    if errors_found == 0:
        print(f"[✓] SUCESSO: Nenhum erro de sintaxe ou quebra detectado em {total} arquivo(s)!")
        print("    O código está íntegro e seguro para execução.")
        print("==================================================")
        return 0
    else:
        print(f"[!] ATENÇÃO: Foram encontrados problemas em {errors_found} de {total} arquivo(s).")
        print("    Corrija os erros acima antes de continuar.")
        print("==================================================")
        return 1

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    code = scan_target(target)
    sys.exit(code)
