"""
REPROCESSAR BANCO - Pula coleta, usa dados existentes
Fluxo: DB → GPT → DB → Sheets (sem coletar!)
"""

import sys
from config import CONFIG
from database import Database
from analisador import AnalisadorGPT
from sheets_reporter import GeradorRelatorioSheets
from datetime import datetime


def banner():
    print("\n" + "=" * 70)
    print("  📊 REPROCESSAR DADOS DO BANCO")
    print("  Pula coleta → Usa dados salvos → Gera planilha")
    print("=" * 70 + "\n")


def listar_perfis(db):
    """Lista perfis disponíveis no banco"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, seguidores, total_posts, data_ultima_atualizacao
            FROM perfis
            WHERE ativo = 1
            ORDER BY data_ultima_atualizacao DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def menu_perfis(perfis):
    """Menu para escolher perfil"""
    if not perfis:
        print("❌ Nenhum perfil no banco!")
        print("   Execute main.py primeiro para coletar dados.\n")
        sys.exit(1)

    print("📋 Perfis no banco:")
    print("-" * 70)
    for i, p in enumerate(perfis, 1):
        print(f"  {i}. {p['username']}")
        print(f"     Seguidores: {p['seguidores']}")
        print(f"     Posts: {p['total_posts']}")
        print(f"     Última atualização: {p['data_ultima_atualizacao']}")
        print()

    print("  0. ❌ SAIR")
    print("-" * 70)

    while True:
        try:
            escolha = int(input("\n👉 Escolha um perfil: "))
            if escolha == 0:
                sys.exit(0)
            if 1 <= escolha <= len(perfis):
                return perfis[escolha - 1]
            print("❌ Opção inválida!")
        except ValueError:
            print("❌ Digite um número!")
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            sys.exit(0)


def reprocessar_perfil(perfil_id, perfil_username, db):
    """Reprocessa perfil: analisa comentários e gera planilha"""

    print(f"\n{'=' * 70}")
    print(f"🎯 REPROCESSANDO: {perfil_username}")
    print(f"{'=' * 70}\n")

    # Estatísticas do banco
    stats = db.get_estatisticas_gerais(perfil_id)
    print(f"📊 Dados no banco:")
    print(f"   • Posts: {stats.get('total_posts', 0)}")
    print(f"   • Comentários: {stats.get('total_comentarios', 0)}")
    print(f"   • Usuários únicos: {stats.get('total_usuarios_unicos', 0)}")

    # Verifica comentários não analisados
    comentarios_pendentes = db.buscar_comentarios_nao_analisados(perfil_id)

    if comentarios_pendentes:
        print(f"\n🤖 Analisando {len(comentarios_pendentes)} comentários com GPT-4...")

        analisador = AnalisadorGPT()

        for i, comentario in enumerate(comentarios_pendentes, 1):
            print(f"  [{i}/{len(comentarios_pendentes)}] {comentario['texto'][:50]}...", end='\r')
            analise = analisador.analisar_comentario(comentario['texto'])
            db.inserir_analise(comentario['id'], analise, 0.0)

        print(f"\n✅ Análises concluídas!")
        print(f"💰 Custo: ~${analisador.custo_estimado:.4f}")
    else:
        print(f"\n✅ Todos os comentários já foram analisados!")

    # Gera planilha
    print(f"\n📊 Gerando Google Sheets...")

    # Pega comentários completos
    comentarios = db.get_comentarios_completos(perfil_id)

    # Pega posts do banco
    posts_do_banco = []
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT post_id, codigo, url, tipo, likes, comentarios_count, data_post, caption
            FROM posts
            WHERE perfil_id = ?
            ORDER BY data_post DESC
        """, (perfil_id,))

        for row in cursor.fetchall():
            posts_do_banco.append({
                'id': row[0],
                'codigo': row[1],
                'url': row[2],
                'tipo': row[3],
                'likes': row[4],
                'comentarios_count': row[5],
                'data': row[6],
                'caption': row[7]
            })

    # Monta dados completos
    dados_completos = {
        'perfil': {
            'username': perfil_username,
            'seguidores': 0,
            'total_posts': stats.get('total_posts', 0)
        },
        'posts': posts_do_banco
    }

    resumo_analise = {
        'total_comentarios': len(comentarios),
        'sentimentos': stats.get('sentimentos', {}),
        'sentimento_percentual': {},
    }

    total = len(comentarios) or 1
    for sent, count in stats.get('sentimentos', {}).items():
        resumo_analise['sentimento_percentual'][sent] = round(count / total * 100, 1)

    # Gera planilha
    try:
        gerador_sheets = GeradorRelatorioSheets()
        url = gerador_sheets.criar_relatorio_completo(
            dados_completos,
            comentarios,
            resumo_analise,
            [],
            perfil_nome=perfil_username
        )

        if url:
            print(f"✅ Planilha criada com sucesso!")
            print(f"🔗 {url}")
        else:
            print(f"⚠️ Planilha não foi criada (erro desconhecido)")

    except Exception as e:
        print(f"❌ Erro ao gerar planilha: {e}")
        print(f"\n💡 Verifique:")
        print(f"   • credentials.json está válido?")
        print(f"   • Google Sheets API está ativada?")
        print(f"   • Service account tem permissão?")

    # Gera resumo executivo
    print(f"\n📄 Gerando resumo executivo...")
    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%M")
    filename = f"resumo_executivo_{perfil_username.replace('@', '')}_{timestamp}.txt"

    top_usuarios = db.get_top_usuarios(perfil_id, limit=5)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("📊 RESUMO EXECUTIVO - ANÁLISE DE INSTAGRAM\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"PERFIL: {perfil_username}\n")
        f.write(f"DATA: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n")

        f.write("📈 NÚMEROS GERAIS\n")
        f.write(f"  • Posts: {stats.get('total_posts', 0)}\n")
        f.write(f"  • Comentários: {stats.get('total_comentarios', 0)}\n")
        f.write(f"  • Usuários únicos: {stats.get('total_usuarios_unicos', 0)}\n\n")

        sentimentos = stats.get('sentimentos', {})
        if sentimentos:
            f.write("😊 SENTIMENTOS\n")
            total = sum(sentimentos.values()) or 1
            for sent, count in sentimentos.items():
                perc = (count / total) * 100
                emoji = "😊" if sent == "positivo" else "😐" if sent == "neutro" else "😞"
                f.write(f"  {emoji} {sent}: {count} ({perc:.1f}%)\n")
            f.write("\n")

        if top_usuarios:
            f.write("👥 TOP USUÁRIOS ATIVOS\n")
            for i, usuario in enumerate(top_usuarios, 1):
                f.write(f"  {i}. @{usuario['usuario']}\n")
                f.write(f"     • {usuario['total_comentarios']} comentários\n\n")

    print(f"✅ Resumo salvo: {filename}")


def main():
    banner()

    # Inicializa banco
    db = Database(CONFIG["DATABASE_PATH"])

    # Lista perfis disponíveis
    perfis = listar_perfis(db)

    if not perfis:
        return

    # Escolhe perfil
    perfil = menu_perfis(perfis)

    # Reprocessa
    reprocessar_perfil(perfil['id'], perfil['username'], db)

    print(f"\n{'=' * 70}")
    print(f"✅ REPROCESSAMENTO CONCLUÍDO!")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
