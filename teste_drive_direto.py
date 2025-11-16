"""
TESTE FINAL - Usar planilha existente
"""

import gspread
from google.oauth2.service_account import Credentials
from config import CONFIG

print("\n🧪 TESTE FINAL - PLANILHA EXISTENTE")
print("=" * 60)

# Verifica se tem PLANILHA_ID
planilha_id = CONFIG.get("PLANILHA_ID", "")

if not planilha_id:
    print("❌ PLANILHA_ID não encontrado no config.py!")
    exit()

print(f"✅ PLANILHA_ID: {planilha_id}")

# Conecta
try:
    print("\n🔗 Conectando ao Google Sheets...")

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file(
        'credentials.json',
        scopes=scopes
    )

    client = gspread.authorize(creds)
    print("✅ Conectado!")

    # Tenta abrir a planilha
    print(f"\n📂 Abrindo planilha...")

    spreadsheet = client.open_by_key(planilha_id)

    print(f"✅ Planilha aberta com sucesso!")
    print(f"📝 Nome: {spreadsheet.title}")
    print(f"🔗 URL: {spreadsheet.url}")

    # Testa escrita
    print("\n✍️  Testando escrita...")

    worksheet = spreadsheet.get_worksheet(0)
    worksheet.update('A1', [['TESTE', 'Funcionou!']])

    print("✅ Escrita funcionou!")
    print("\n💡 Abra a planilha e veja 'TESTE' escrito!")

    # Limpa
    print("\n🧹 Limpando...")
    worksheet.update('A1', [['', '']])

    print("\n" + "=" * 60)
    print("🎉 TUDO PERFEITO!")
    print("=" * 60)
    print("\n✅ PODE RODAR: python main.py")

except gspread.exceptions.SpreadsheetNotFound:
    print(f"\n❌ Planilha NÃO encontrada!")
    print(f"\n📧 Compartilhe com:")

    import json

    with open('credentials.json', 'r') as f:
        cred_data = json.load(f)
        print(f"   {cred_data['client_email']}")

    print(f"\n💡 Permissão: Editor")

except Exception as e:
    print(f"\n❌ ERRO: {e}")

print()