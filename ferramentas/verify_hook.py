import sys
import json
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def main():
    try:
        raw_input = sys.stdin.read()
        data = json.loads(raw_input) if raw_input.strip() else {}
    except Exception:
        data = {}

    # Check if toolCall exists (PostToolUse)
    tool_call = data.get("toolCall", {})
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args", {})
    
    # If a file was written/edited, verify it if possible
    if tool_name in ["write_file", "edit_file"]:
        path = args.get("Path", "")
        if path and os.path.exists(path):
            verifier = os.path.join(os.path.dirname(__file__), "verify_safety.py")
            if os.path.exists(verifier):
                # Run lightweight syntax check
                import subprocess
                subprocess.run([sys.executable, verifier, path], capture_output=True)
                
    # If PreInvocation, inject safety reminder
    if "invocationNum" in data:
        response = {
            "injectSteps": [
                {
                    "ephemeralMessage": "🛡️ VERIFICAÇÃO DE SEGURANÇA: Certifique-se de que as alterações propostas não quebrem o código existente. Execute a validação de integridade antes de concluir."
                }
            ]
        }
        print(json.dumps(response))
        return

    # Standard exit for other hooks
    print(json.dumps({}))

if __name__ == "__main__":
    main()
