"""
Testa se o .env está sendo lido corretamente
"""

import os
from pathlib import Path

print("\n" + "=" * 70)
print("🔍 TESTANDO LEITURA DO .ENV")
print("=" * 70 + "\n")

# Verifica se arquivo existe
env_path = Path(__file__).parent / '.env'
print(f"1. Procurando .env em: {env_path}")

if env_path.exists():
    print("   ✅ Arquivo .env EXISTE!\n")

    print("2. Conteúdo do .env:")
    print("   " + "-" * 66)
    with open(env_path, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        for i, linha in enumerate(linhas, 1):
            # Oculta senhas
            if '=' in linha and not linha.strip().startswith('#'):
                chave, valor = linha.split('=', 1)
                if 'PASS' in chave or 'KEY' in chave:
                    print(f"   {i:2d}. {chave}=***OCULTO***")
                else:
                    print(f"   {i:2d}. {linha.strip()}")
            else:
                print(f"   {i:2d}. {linha.strip()}")
    print("   " + "-" * 66 + "\n")
else:
    print("   ❌ Arquivo .env NÃO EXISTE!\n")
    print("   Crie o arquivo primeiro:\n")
    print("   python configurar_local.py\n")
    exit(1)

# Tenta carregar com python-dotenv
print("3. Testando python-dotenv:")
try:
    from dotenv import load_dotenv
    print("   ✅ python-dotenv instalado!\n")

    load_dotenv(env_path)
    print("   ✅ .env carregado!\n")

except ImportError:
    print("   ❌ python-dotenv NÃO instalado!\n")
    print("   Instale com: pip install python-dotenv\n")
    exit(1)

# Verifica se variáveis foram carregadas
print("4. Verificando variáveis de ambiente:")
print("   " + "-" * 66)

variaveis = [
    "INSTAGRAM_USER",
    "INSTAGRAM_PASS",
    "OPENAI_KEY",
    "PLANILHA_ID",
    "PROXY_HOST",
    "PROXY_PORT",
    "PROXY_USER",
    "PROXY_PASS"
]

for var in variaveis:
    valor = os.getenv(var, "")
    if valor:
        if 'PASS' in var or 'KEY' in var:
            print(f"   ✅ {var:20s} = ***{'*' * len(valor)}*** ({len(valor)} caracteres)")
        else:
            print(f"   ✅ {var:20s} = {valor}")
    else:
        print(f"   ⚠️  {var:20s} = (vazio)")

print("   " + "-" * 66 + "\n")

# Testa config.py
print("5. Testando config.py:")
try:
    from config import CONFIG
    print("   ✅ config.py importado!\n")

    print("   Valores no CONFIG:")
    print("   " + "-" * 66)
    for var in ["INSTAGRAM_USER", "INSTAGRAM_PASS", "OPENAI_KEY", "PLANILHA_ID"]:
        valor = CONFIG.get(var, "")
        if valor:
            if 'PASS' in var or 'KEY' in var:
                print(f"   ✅ {var:20s} = ***CONFIGURADO***")
            else:
                print(f"   ✅ {var:20s} = {valor}")
        else:
            print(f"   ❌ {var:20s} = VAZIO!")
    print("   " + "-" * 66 + "\n")

except Exception as e:
    print(f"   ❌ Erro ao importar config.py: {e}\n")

print("=" * 70)
print("✅ DIAGNÓSTICO COMPLETO!")
print("=" * 70 + "\n")
