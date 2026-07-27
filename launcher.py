import os
import sys
import subprocess
import urllib.request

# URLs do seu repositório no GitHub
URL_VERSAO = "https://raw.githubusercontent.com/sharlomcobranca/cobranca-pro-update/refs/heads/main/version.txt"
URL_CODIGO = "https://raw.githubusercontent.com/sharlomcobranca/cobranca-pro-update/refs/heads/main/main.py"
VERSAO_LOCAL = "1.0.0"

def atualizar():
    try:
        # Tenta baixar a versão remota do GitHub
        with urllib.request.urlopen(URL_VERSAO, timeout=5) as response:
            versao_remota = response.read().decode('utf-8').strip()
            
        if versao_remota != VERSAO_LOCAL:
            # Baixa a nova versão do main.py
            with urllib.request.urlopen(URL_CODIGO, timeout=10) as response:
                codigo_novo = response.read().decode('utf-8')
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(codigo_novo)
    except Exception as e:
        print(f"Modo offline ou erro na atualização: {e}")

if __name__ == "__main__":
    atualizar()
    
    # Executa o main.py usando o interpretador do Python do sistema
    if os.path.exists("main.py"):
        subprocess.Popen(["python", "main.py"])
    else:
        print("Erro: Arquivo main.py não encontrado!")