"""
ANALISADOR DE COMENTÁRIOS DO INSTAGRAM V2.0
Com SQLite, Análise Incremental e Menu Interativo
"""

import sys
import os
from datetime import datetime
from config import CONFIG
from database import Database
from coletor import ColetorInstagram
from analisador import AnalisadorGPT
from sheets_reporter import GeradorRelatorioSheets


def banner():
    print("\n" + "=" * 70)
    print("  📊 ANALISADOR DE COMENTÁRIOS DO INSTAGRAM v2.0")
    print("  💾 SQLite + Incremental + Multi-Perfis + GPT-4")
    print("=" * 70 + "\n")


def carregar_perfis():
    """Carrega perfis do arquivo perfis.txt"""
    try:
        with open('perfis.txt', 'r', encoding='utf-8') as f:
            perfis = [linha.strip() for linha in f if linha.strip() and not linha.startswith('#')]
        return perfis
    except FileNotFoundError:
        print("⚠️  Arquivo perfis.txt não encontrado!")
        print("   Criando com perfil padrão do config.py...")

        # Cria arquivo com perfis do config
        with open('perfis.txt', 'w', encoding='utf-8') as f:
            for perfil in CONFIG.get("PERFIS_ALVO", []):
                f.write(f"{perfil}\n")

        return CONFIG.get("PERFIS_ALVO", [])


def menu_selecao_perfis(perfis):
    """Menu para escolher quais perfis analisar"""
    print("\n" + "=" * 70)
    print("  📋 PERFIS DISPONÍVEIS")
    print("=" * 70)

    for i, perfil in enumerate(perfis, 1):
        print(f"  {i}. {perfil}")

    print(f"\n  {len(perfis) + 1}. 🔄 ANALISAR TODOS")
    print(f"  {len(perfis) + 2}. ➕ ADICIONAR NOVO PERFIL")
    print(f"  0. ❌ SAIR")

    print("\n" + "=" * 70)

    while True:
        try:
            escolha = input("\n👉 Escolha uma opção: ").strip()

            if escolha == '0':
                print("\n👋 Até logo!")
                sys.exit(0)

            escolha_num = int(escolha)

            if escolha_num == len(perfis) + 1:
                return perfis  # Todos

            elif escolha_num == len(perfis) + 2:
                novo_perfil = input("\n📝 Digite o @ do perfil (ex: @admiravelcafe): ").strip()
                if novo_perfil:
                    if not novo_perfil.startswith('@'):
                        novo_perfil = '@' + novo_perfil

                    # Adiciona no arquivo
                    with open('perfis.txt', 'a', encoding='utf-8') as f:
                        f.write(f"\n{novo_perfil}")

                    print(f"✅ Perfil {novo_perfil} adicionado!")
                    return [novo_perfil]

            elif 1 <= escolha_num <= len(perfis):
                return [perfis[escolha_num - 1]]

            else:
                print("❌ Opção inválida!")

        except ValueError:
            print("❌ Digite um número válido!")
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            sys.exit(0)


def analisar_perfil(perfil_username, db, coletor, analisador):
    """Analisa um perfil com modo incremental"""

    print(f"\n{'=' * 70}")
    print(f"🎯 ANALISANDO: {perfil_username}")
    print(f"{'=' * 70}")

    # Verifica se perfil já existe no banco
    perfil_existente = db.buscar_perfil(perfil_username)

    if perfil_existente:
        print(f"📂 Perfil encontrado no banco (ID: {perfil_existente['id']})")
        print(f"📅 Última atualização: {perfil_existente['data_ultima_atualizacao']}")
        perfil_id = perfil_existente['id']
        modo = "incremental"
    else:
        print(f"🆕 Perfil novo! Primeira análise completa.")
        perfil_id = None
        modo = "completa"

    # Coleta dados do perfil
    print(f"\n{'=' * 70}")
    print(f"🎯 COLETA DE DADOS - Modo: {modo.upper()}")
    print(f"{'=' * 70}")

    dados = coletor.coletar_tudo(perfil_username, CONFIG["POSTS_ANALISAR"])

    # Salva/atualiza perfil no banco
    perfil_id = db.inserir_perfil(dados['perfil'])

    # Processa posts e comentários (MODO INCREMENTAL!)
    print(f"\n💾 Salvando dados no banco...")

    posts_novos = 0
    comentarios_novos = 0
    comentarios_atualizados = 0

    for post in dados['posts']:
        post_id = db.inserir_post(perfil_id, post)

        # Pega comentários já existentes deste post
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT comentario_id FROM comentarios WHERE post_id = ?
            """, (post_id,))
            comentarios_existentes = {row[0] for row in cursor.fetchall()}

        # Insere apenas comentários novos ou atualiza existentes
        for comentario in post['comentarios']:
            if comentario['id'] in comentarios_existentes:
                comentarios_atualizados += 1
            else:
                comentarios_novos += 1

            db.inserir_comentario(post_id, comentario)

    print(f"✅ Posts processados: {len(dados['posts'])}")
    print(f"✅ Comentários novos: {comentarios_novos}")
    print(f"✅ Comentários atualizados: {comentarios_atualizados}")

    # Analisa APENAS comentários não analisados
    print(f"\n🤖 Analisando comentários com GPT-4...")

    comentarios_pendentes = db.buscar_comentarios_nao_analisados(perfil_id)

    if comentarios_pendentes:
        print(f"📝 {len(comentarios_pendentes)} comentários novos para analisar")

        for i, comentario in enumerate(comentarios_pendentes, 1):
            print(f"  [{i}/{len(comentarios_pendentes)}] Analisando...", end='\r')
            analise = analisador.analisar_comentario(comentario['texto'])
            db.inserir_analise(comentario['id'], analise, 0.0)

        print(f"\n✅ Análises concluídas!")
        print(f"💰 Custo: ~${analisador.custo_estimado:.4f}")
    else:
        print(f"✅ Nenhum comentário novo! Tudo já foi analisado.")
        print(f"💰 Custo: $0.00 (economia total!)")

    return perfil_id, comentarios_novos, len(comentarios_pendentes)


def gerar_resumo_executivo(perfil_username, perfil_id, db):
    """Gera arquivo de resumo executivo em texto"""

    stats = db.get_estatisticas_gerais(perfil_id)
    top_usuarios = db.get_top_usuarios(perfil_id, limit=5)

    timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%M")
    filename = f"resumo_executivo_{perfil_username.replace('@', '')}_{timestamp}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("📊 RESUMO EXECUTIVO - ANÁLISE DE INSTAGRAM\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"PERFIL: {perfil_username}\n")
        f.write(f"DATA: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n")

        f.write("=" * 70 + "\n")
        f.write("📈 NÚMEROS GERAIS\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"  • Posts: {stats.get('total_posts', 0)}\n")
        f.write(f"  • Comentários: {stats.get('total_comentarios', 0)}\n")
        f.write(f"  • Usuários únicos: {stats.get('total_usuarios_unicos', 0)}\n\n")

        f.write("=" * 70 + "\n")
        f.write("😊 SENTIMENTOS\n")
        f.write("=" * 70 + "\n\n")

        sentimentos = stats.get('sentimentos', {})
        total = sum(sentimentos.values()) or 1

        for sent, count in sentimentos.items():
            perc = (count / total) * 100
            emoji = "😊" if sent == "positivo" else "😐" if sent == "neutro" else "😞"
            f.write(f"  {emoji} {sent}: {count} ({perc:.1f}%)\n")

        f.write("\n")

        # SÓ MOSTRA TOP USUÁRIOS SE TIVER COMENTÁRIOS
        if top_usuarios:
            f.write("=" * 70 + "\n")
            f.write("👥 TOP USUÁRIOS ATIVOS\n")
            f.write("=" * 70 + "\n\n")

            for i, usuario in enumerate(top_usuarios, 1):
                f.write(f"  {i}. @{usuario['usuario']}\n")
                f.write(f"     • {usuario['total_comentarios']} comentários\n")
                media = usuario.get('media_likes') or 0
                f.write(f"     • Média: {media:.1f} likes\n\n")

        f.write("=" * 70 + "\n")
        f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write("=" * 70 + "\n")

    return filename


def main():
    banner()

    # Carrega perfis disponíveis
    perfis_disponiveis = carregar_perfis()

    if not perfis_disponiveis:
        print("❌ Nenhum perfil configurado!")
        print("   Adicione perfis no arquivo perfis.txt")
        return

    # Menu de seleção
    perfis_escolhidos = menu_selecao_perfis(perfis_disponiveis)

    # Inicializa componentes
    print(f"\n📊 Inicializando banco de dados...")
    db = Database(CONFIG["DATABASE_PATH"])

    print(f"🔐 Fazendo login no Instagram...")
    coletor = ColetorInstagram()

    if not coletor.fazer_login():
        print("❌ Erro no login. Verifique config.py")
        return

    analisador = AnalisadorGPT()

    # Processa cada perfil escolhido
    resultados = []

    for perfil in perfis_escolhidos:
        try:
            perfil_id, comentarios_novos, analises = analisar_perfil(
                perfil, db, coletor, analisador
            )

            resultados.append({
                'perfil': perfil,
                'perfil_id': perfil_id,
                'comentarios_novos': comentarios_novos,
                'analises': analises
            })

        except Exception as e:
            print(f"\n❌ Erro ao analisar {perfil}: {e}")
            continue

    # ========================================================================
    # GERA RELATÓRIOS - PARTE ATUALIZADA!
    # ========================================================================

    print(f"\n{'=' * 70}")
    print(f"📊 GERANDO RELATÓRIOS")
    print(f"{'=' * 70}")

    gerador_sheets = GeradorRelatorioSheets()

    for resultado in resultados:
        perfil = resultado['perfil']
        perfil_id = resultado['perfil_id']

        print(f"\n🎯 Perfil: {perfil}")

        # Resumo executivo
        print(f"📄 Gerando resumo executivo...")
        arquivo_resumo = gerar_resumo_executivo(perfil, perfil_id, db)
        print(f"✅ Resumo salvo: {arquivo_resumo}")

        # Google Sheets
        print(f"📊 Atualizando Google Sheets...")

        # Pega dados do banco
        comentarios = db.get_comentarios_completos(perfil_id)
        stats = db.get_estatisticas_gerais(perfil_id)

        # Pega POSTS do banco
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
                'username': perfil,
                'seguidores': 0,
                'total_posts': stats.get('total_posts', 0)
            },
            'posts': posts_do_banco
        }

        resumo_analise = {
            'total_comentarios': len(comentarios),
            'sentimentos': stats.get('sentimentos', {}),
            'sentimento_percentual': {},
            'categorias': {},
            'topicos': {},
            'top_palavras_chave': [],
            'urgencias': 0,
            'intencao_compra': 0,
            'custo_analise': 0
        }

        total = len(comentarios) or 1
        for sent, count in stats.get('sentimentos', {}).items():
            resumo_analise['sentimento_percentual'][sent] = round(count / total * 100, 1)

        url = gerador_sheets.criar_relatorio_completo(
            dados_completos,
            comentarios,
            resumo_analise,
            [],
            perfil_nome=perfil
        )

        if url:
            print(f"✅ Planilha atualizada!")
            print(f"🔗 {url}")

    # ========================================================================
    # FIM DA PARTE ATUALIZADA
    # ========================================================================

    # Resumo final
    print(f"\n{'=' * 70}")
    print(f"✅ ANÁLISE CONCLUÍDA!")
    print(f"{'=' * 70}\n")

    for resultado in resultados:
        print(f"  📊 {resultado['perfil']}")
        print(f"     • {resultado['comentarios_novos']} comentários novos coletados")
        print(f"     • {resultado['analises']} análises realizadas")

    print(f"\n💰 Custo total GPT: ~${analisador.custo_estimado:.4f}")
    print(f"\n{'=' * 70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        if CONFIG.get("DEBUG"):
            import traceback

            traceback.print_exc()
        sys.exit(1)