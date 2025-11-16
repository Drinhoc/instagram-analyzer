import gspread
from google.oauth2.service_account import Credentials

print("\n🧪 TESTANDO GOOGLE SHEETS...")
print("="*60)

try:
    # Configura credenciais
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    print("📂 Carregando credentials.json...")
    creds = Credentials.from_service_account_file(
        'credentials.json',
        scopes=scopes
    )
    
    print("🔗 Conectando ao Google Sheets...")
    gc = gspread.authorize(creds)
    
    print("📊 Tentando criar planilha de teste...")
    sheet = gc.create("TESTE - Instagram Analyzer")
    
    print(f"\n✅ SUCESSO! Planilha criada!")
    print(f"🔗 URL: {sheet.url}")
    
    # Pega o email do config
    from config import CONFIG
    email = CONFIG.get("COMPARTILHAR_COM_EMAIL", "")
    
    if email:
        print(f"\n📧 Compartilhando com: {email}")
        sheet.share(email, perm_type='user', role='writer')
        print("✅ Compartilhado com sucesso!")
        print(f"\n🎉 Verifique seu Gmail ({email})!")
        print("   A planilha deve aparecer no seu Drive!")
    else:
        print("\n⚠️  Nenhum email configurado em COMPARTILHAR_COM_EMAIL")
        print("   A planilha foi criada mas não compartilhada.")
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*60)
    
    # Deleta a planilha de teste
    print("\n🗑️  Deletando planilha de teste...")
    gc.del_spreadsheet(sheet.id)
    print("✅ Limpeza concluída!")

except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print("\nVerifique:")
    print("1. credentials.json está na pasta?")
    print("2. APIs estão ativadas no Google Cloud?")
    print("3. Email está correto no config.py?")

print()