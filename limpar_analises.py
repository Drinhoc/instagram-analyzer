"""
Limpa análises antigas para permitir re-análise
"""

import sqlite3
import sys

db_path = "instagram_analytics.db"

print("=" * 70)
print("🧹 LIMPAR ANÁLISES ANTIGAS")
print("=" * 70)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verifica quantas análises existem
    cursor.execute("SELECT COUNT(*) FROM analises")
    total = cursor.fetchone()[0]

    print(f"\n📊 Total de análises no banco: {total}")

    if total == 0:
        print("✅ Nenhuma análise para limpar!")
        conn.close()
        sys.exit(0)

    resposta = input(f"\n⚠️  Tem certeza que deseja DELETAR {total} análises? (sim/nao): ")

    if resposta.lower() != 'sim':
        print("❌ Operação cancelada!")
        conn.close()
        sys.exit(0)

    # Deleta todas as análises
    cursor.execute("DELETE FROM analises")
    conn.commit()

    # Marca comentários como não analisados
    cursor.execute("UPDATE comentarios SET analisado = 0")
    conn.commit()

    print(f"\n✅ {total} análises deletadas com sucesso!")
    print("✅ Comentários marcados como não analisados!")
    print("\n💡 Agora execute: python reprocessar_banco.py")
    print("   Ou: python main.py (para nova coleta completa)")

    conn.close()

except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
