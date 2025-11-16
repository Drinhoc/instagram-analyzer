from database import Database

db = Database("instagram_analytics.db")

# Ver resumo
print("\n" + "="*60)
print("📊 RESUMO DOS DADOS NO BANCO")
print("="*60)

stats = db.get_estatisticas_gerais(1)
print(f"\n✅ Posts coletados: {stats.get('total_posts', 0)}")
print(f"✅ Comentários coletados: {stats.get('total_comentarios', 0)}")
print(f"✅ Usuários únicos: {stats.get('total_usuarios_unicos', 0)}")

# Sentimentos
print("\n📈 SENTIMENTOS:")
for sentimento, count in stats.get('sentimentos', {}).items():
    print(f"   {sentimento}: {count}")

# Ver alguns comentários
print("\n" + "="*60)
print("💬 ÚLTIMOS COMENTÁRIOS ANALISADOS")
print("="*60)

comentarios = db.get_comentarios_completos(1, limit=10)
for i, c in enumerate(comentarios[:5], 1):
    print(f"\n{i}. @{c['usuario']}")
    print(f"   Comentário: {c['texto'][:80]}...")
    print(f"   Sentimento: {c['sentimento']} | Categoria: {c['categoria']}")
    print(f"   Tópico: {c['topico']}")

print("\n" + "="*60)
print(f"✅ Total de {len(comentarios)} comentários no banco!")
print("="*60 + "\n")