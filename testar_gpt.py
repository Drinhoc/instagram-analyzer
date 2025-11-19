"""
Teste rápido do GPT para verificar se está analisando corretamente
"""

import sys
import logging
from analisador import AnalisadorGPT

# Setup logging
logging.basicConfig(level=logging.INFO)

print("=" * 70)
print("🧪 TESTE DE ANÁLISE GPT")
print("=" * 70)

# Testa alguns comentários
comentarios_teste = [
    "Ahhhh que turma linda!!!",
    "❤️😍 Amei demais!",
    "Péssimo atendimento, muito caro",
    "Qual o preço desse produto?",
    "Muito top! Quero comprar"
]

try:
    print("\n📞 Inicializando AnalisadorGPT...")
    analisador = AnalisadorGPT()
    print("✅ Analisador inicializado!")

    print(f"\n📝 Testando {len(comentarios_teste)} comentários...\n")

    for i, comentario in enumerate(comentarios_teste, 1):
        print(f"\n{'='*70}")
        print(f"COMENTÁRIO {i}: \"{comentario}\"")
        print(f"{'='*70}")

        try:
            analise = analisador.analisar_comentario(comentario)

            print(f"✅ Análise recebida:")
            print(f"   Sentimento: {analise.get('sentimento')}")
            print(f"   Categoria: {analise.get('categoria')}")
            print(f"   Tópico: {analise.get('topico')}")
            print(f"   Urgência: {analise.get('urgencia')}")
            print(f"   Intenção: {analise.get('intent')}")
            print(f"   Resposta: {analise.get('resposta_sugerida')}")

        except Exception as e:
            print(f"❌ Erro ao analisar: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"💰 Custo total estimado: ${analisador.custo_estimado:.6f}")
    print(f"📊 Total analisado: {analisador.total_analisado}")
    print(f"{'='*70}\n")

except Exception as e:
    print(f"\n❌ ERRO FATAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
