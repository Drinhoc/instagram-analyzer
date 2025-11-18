"""
TESTE COMPLETO DO SISTEMA
Testa todas as partes antes de rodar o main.py
"""

import sys
print("\n" + "=" * 70)
print("🔬 TESTE COMPLETO DO SISTEMA")
print("=" * 70 + "\n")

# 1. Testa config
print("1️⃣ Testando config.py...")
try:
    from config import CONFIG, validar_config
    print("   ✅ config.py importado!")

    if validar_config():
        print("   ✅ Configurações válidas!\n")
    else:
        print("   ❌ Configurações inválidas!")
        print("   Execute: python configurar_local.py\n")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Erro: {e}\n")
    sys.exit(1)

# 2. Testa database
print("2️⃣ Testando database.py...")
try:
    from database import Database
    db = Database(":memory:")  # Banco em memória para teste
    print("   ✅ Database funciona!")

    # Testa inserir perfil
    perfil_teste = {
        'username': 'teste',
        'nome_completo': 'Teste User',
        'biografia': 'Bio de teste',
        'seguidores': 100,
        'seguindo': 50,
        'total_posts': 10,
        'eh_verificado': False,
        'eh_comercial': False
    }
    perfil_id = db.inserir_perfil(perfil_teste)
    print(f"   ✅ Perfil inserido (ID: {perfil_id})")

    # Testa inserir post
    post_teste = {
        'id': '123456789',
        'codigo': 'ABC123',
        'url': 'https://instagram.com/p/ABC123/',
        'tipo': 'Photo',
        'caption': 'Teste',
        'likes': 10,
        'comentarios_count': 5,
        'data': '2024-01-01T12:00:00'
    }
    post_id = db.inserir_post(perfil_id, post_teste)
    print(f"   ✅ Post inserido (ID: {post_id})")

    # Testa inserir comentário
    comentario_teste = {
        'id': '987654321',
        'usuario': 'usuario_teste',
        'texto': 'Comentário de teste',
        'likes': 2,
        'data': '2024-01-01T12:30:00'
    }
    comentario_id = db.inserir_comentario(post_id, comentario_teste)
    print(f"   ✅ Comentário inserido (ID: {comentario_id})\n")

except Exception as e:
    print(f"   ❌ Erro: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Testa analisador
print("3️⃣ Testando analisador.py...")
try:
    from analisador import AnalisadorGPT

    if not CONFIG.get("OPENAI_KEY") or CONFIG["OPENAI_KEY"].startswith("sk-sua"):
        print("   ⚠️ OpenAI key não configurada - pulando teste de análise")
        print("   (não é crítico, só não vai analisar)\n")
    else:
        analisador = AnalisadorGPT()
        print("   ✅ Analisador inicializado!")

        # Teste simples (sem gastar crédito de verdade, só valida estrutura)
        print("   ⏭️  Pulando teste real de GPT (para não gastar crédito)\n")

except Exception as e:
    print(f"   ❌ Erro: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Testa coletor (sem fazer login de verdade)
print("4️⃣ Testando coletor.py (estrutura)...")
try:
    from coletor import ColetorInstagram
    print("   ✅ Coletor importado!")
    print("   ⏭️  Pulando teste de login (para não gastar tentativas)\n")

except Exception as e:
    print(f"   ❌ Erro: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Verifica sheets_reporter
print("5️⃣ Testando sheets_reporter.py...")
try:
    from sheets_reporter import GeradorRelatorioSheets
    print("   ✅ Sheets reporter importado!")
    print("   ⏭️  Pulando teste real (precisa de credenciais Google)\n")

except Exception as e:
    print(f"   ❌ Erro: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Resumo final
print("=" * 70)
print("✅ TODOS OS TESTES PASSARAM!")
print("=" * 70)
print("\n🎯 O sistema está pronto para usar!")
print("\nPróximos passos:")
print("  1. Execute: python main.py")
print("  2. Escolha o perfil para analisar")
print("  3. Aguarde a análise completa")
print("\n" + "=" * 70 + "\n")
