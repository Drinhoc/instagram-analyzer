"""
Script para salvar sessão do Instagram
Roda no seu PC LOCAL antes de fazer deploy
"""

import instagrapi
import json

print("🔐 Fazendo login no Instagram...")

client = instagrapi.Client()
client.delay_range = [1, 3]

# Suas credenciais
USERNAME = "papo.fiadobr@gmail.com"
PASSWORD = "@Jacarecoruja13"

try:
    # Faz login
    client.login(USERNAME, PASSWORD)
    print("✅ Login realizado com sucesso!")
    
    # Salva a sessão
    session_data = client.get_settings()
    
    with open("session.json", "w") as f:
        json.dump(session_data, f, indent=2)
    
    print("✅ Sessão salva em session.json!")
    print("\n📌 Agora faça:")
    print("1. git add session.json")
    print("2. git commit -m 'Add session file'")
    print("3. git push origin main")
    print("\nDepois atualize o app.py!")
    
except Exception as e:
    print(f"❌ Erro no login: {e}")
    print("\n💡 Se der erro, tente:")
    print("- Verificar usuário/senha")
    print("- Usar VPN")
    print("- Aguardar alguns minutos")
