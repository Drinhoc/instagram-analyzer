"""
TESTE ESPECÍFICO DO GOOGLE SHEETS
Testa APENAS a conexão e criação de planilha
"""

import sys
import os

print("\n" + "=" * 70)
print("🔍 TESTE DE GOOGLE SHEETS")
print("=" * 70 + "\n")

# 1. Verifica credentials.json
print("1️⃣ Verificando credentials.json...")

from config import CONFIG

creds_file = CONFIG["GOOGLE_CREDENTIALS_FILE"]
print(f"   Arquivo: {creds_file}")

if not os.path.exists(creds_file):
    print(f"   ❌ Arquivo não encontrado!")
    print(f"\n💡 Solução:")
    print(f"   1. Baixe credentials.json do Google Cloud Console")
    print(f"   2. Coloque na pasta do projeto")
    sys.exit(1)
else:
    print(f"   ✅ Arquivo existe!")

# Verifica se é JSON válido
try:
    import json
    with open(creds_file, 'r') as f:
        creds_data = json.load(f)
    print(f"   ✅ JSON válido!")
    print(f"   Service Account: {creds_data.get('client_email', 'N/A')}")
    print(f"   Project ID: {creds_data.get('project_id', 'N/A')}")
except Exception as e:
    print(f"   ❌ JSON inválido: {e}")
    sys.exit(1)

# 2. Testa autenticação
print(f"\n2️⃣ Testando autenticação...")

try:
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(creds_file, scopes=scopes)
    gc = gspread.authorize(credentials)

    print(f"   ✅ Autenticação OK!")

except Exception as e:
    print(f"   ❌ Erro de autenticação: {e}")
    print(f"\n💡 Possíveis causas:")
    print(f"   • Service account key expirada")
    print(f"   • Projeto do Google Cloud desabilitado")
    print(f"   • APIs não habilitadas")
    sys.exit(1)

# 3. Testa criação de planilha
print(f"\n3️⃣ Testando criação de planilha...")

try:
    # Cria planilha de teste
    sh = gc.create('TESTE_Instagram_Analyzer')
    print(f"   ✅ Planilha criada!")
    print(f"   URL: {sh.url}")

    # Testa escrita
    worksheet = sh.sheet1
    worksheet.update('A1', 'TESTE OK!')
    print(f"   ✅ Escrita funcionando!")

    # Deleta planilha de teste
    gc.del_spreadsheet(sh.id)
    print(f"   ✅ Planilha de teste deletada!")

except Exception as e:
    print(f"   ❌ Erro ao criar planilha: {e}")
    print(f"\n💡 Possíveis causas:")
    print(f"   • Google Sheets API não habilitada")
    print(f"   • Google Drive API não habilitada")
    print(f"   • Service account sem permissão")
    print(f"\n🔧 Solução:")
    print(f"   1. Vai em: https://console.cloud.google.com/")
    print(f"   2. Habilita Google Sheets API")
    print(f"   3. Habilita Google Drive API")
    print(f"   4. Verifica permissões da Service Account")

    import traceback
    print(f"\n📋 Detalhes do erro:")
    traceback.print_exc()
    sys.exit(1)

# 4. Testa compartilhamento (se tiver PLANILHA_ID)
planilha_id = CONFIG.get("PLANILHA_ID")
if planilha_id:
    print(f"\n4️⃣ Testando acesso à planilha configurada...")
    print(f"   ID: {planilha_id}")

    try:
        sh = gc.open_by_key(planilha_id)
        print(f"   ✅ Planilha acessível!")
        print(f"   Nome: {sh.title}")
        print(f"   URL: {sh.url}")

    except Exception as e:
        print(f"   ❌ Erro ao acessar: {e}")
        print(f"\n💡 Solução:")
        print(f"   • Compartilhe a planilha com: {creds_data.get('client_email')}")
        print(f"   • Dê permissão de Editor")

print(f"\n" + "=" * 70)
print(f"✅ TODOS OS TESTES PASSARAM!")
print(f"=" * 70)
print(f"\n💡 Google Sheets está funcionando perfeitamente!")
print(f"   Agora você pode rodar: python reprocessar_banco.py\n")
