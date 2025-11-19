"""
REPROCESSAR BANCO - Pula coleta, usa dados existentes
Fluxo: DB → GPT → DB → Sheets (sem coletar!)
"""

import sys
import logging
from pathlib import Path
from config import CONFIG
from database import Database
from analisador import AnalisadorGPT
from sheets_reporter import GeradorRelatorioSheets
from datetime import datetime


# Configurar logging
def setup_logging():
    """Configura sistema de logging com arquivo e console"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"reprocessar_banco_{timestamp}.log"

    # Formato detalhado para logs
    log_format = '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Configurar logger raiz
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"=== Iniciando reprocessamento - Log: {log_file} ===")
    return logger


logger = setup_logging()


def banner():
    print("\n" + "=" * 70)
    print("  📊 REPROCESSAR DADOS DO BANCO")
    print("  Pula coleta → Usa dados salvos → Gera planilha")
    print("=" * 70 + "\n")


def listar_perfis(db):
    """Lista perfis disponíveis no banco"""
    try:
        logger.info("Buscando perfis no banco de dados...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, seguidores, total_posts, data_ultima_atualizacao
                FROM perfis
                WHERE ativo = 1
                ORDER BY data_ultima_atualizacao DESC
            """)
            perfis = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Encontrados {len(perfis)} perfis ativos no banco")
            return perfis
    except Exception as e:
        logger.error(f"Erro ao listar perfis do banco: {e}", exc_info=True)
        raise


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
    logger.info(f"Iniciando reprocessamento do perfil: {perfil_username} (ID: {perfil_id})")

    print(f"\n{'=' * 70}")
    print(f"🎯 REPROCESSANDO: {perfil_username}")
    print(f"{'=' * 70}\n")

    # Estatísticas do banco
    try:
        logger.info("Buscando estatísticas gerais do perfil...")
        stats = db.get_estatisticas_gerais(perfil_id)
        logger.info(f"Estatísticas obtidas: {stats}")

        print(f"📊 Dados no banco:")
        print(f"   • Posts: {stats.get('total_posts', 0)}")
        print(f"   • Comentários: {stats.get('total_comentarios', 0)}")
        print(f"   • Usuários únicos: {stats.get('total_usuarios_unicos', 0)}")
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas do perfil {perfil_id}: {e}", exc_info=True)
        print(f"❌ Erro ao buscar estatísticas: {e}")
        raise

    # Verifica comentários não analisados
    try:
        logger.info("Buscando comentários não analisados...")
        comentarios_pendentes = db.buscar_comentarios_nao_analisados(perfil_id)
        logger.info(f"Encontrados {len(comentarios_pendentes)} comentários pendentes de análise")

        if comentarios_pendentes:
            print(f"\n🤖 Analisando {len(comentarios_pendentes)} comentários com GPT-4...")
            logger.info("Iniciando análise com GPT-4...")

            try:
                analisador = AnalisadorGPT()
                logger.info("AnalisadorGPT inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar AnalisadorGPT: {e}", exc_info=True)
                print(f"❌ Erro ao inicializar GPT: {e}")
                print(f"💡 Verifique:")
                print(f"   • OPENAI_API_KEY está configurada no .env?")
                print(f"   • A chave API está válida?")
                raise

            erros_analise = 0
            for i, comentario in enumerate(comentarios_pendentes, 1):
                try:
                    print(f"  [{i}/{len(comentarios_pendentes)}] {comentario['texto'][:50]}...", end='\r')
                    logger.debug(f"Analisando comentário {comentario['id']}: {comentario['texto'][:100]}")

                    analise = analisador.analisar_comentario(comentario['texto'])
                    db.inserir_analise(comentario['id'], analise, 0.0)

                    logger.debug(f"Comentário {comentario['id']} analisado: {analise}")
                except Exception as e:
                    erros_analise += 1
                    logger.error(f"Erro ao analisar comentário {comentario['id']}: {e}", exc_info=True)
                    print(f"\n⚠️ Erro no comentário {i}: {e}")

            print(f"\n✅ Análises concluídas!")
            print(f"💰 Custo: ~${analisador.custo_estimado:.4f}")

            if erros_analise > 0:
                logger.warning(f"Total de erros na análise: {erros_analise}/{len(comentarios_pendentes)}")
                print(f"⚠️ {erros_analise} comentários não foram analisados (veja o log)")
            else:
                logger.info("Todas as análises completadas com sucesso")
        else:
            print(f"\n✅ Todos os comentários já foram analisados!")
            logger.info("Nenhum comentário pendente de análise")

    except Exception as e:
        logger.error(f"Erro ao processar análise de comentários: {e}", exc_info=True)
        print(f"❌ Erro ao analisar comentários: {e}")
        raise

    # Gera planilha
    print(f"\n📊 Gerando Google Sheets...")
    logger.info("Iniciando geração da planilha Google Sheets...")

    # Pega comentários completos
    try:
        logger.info("Buscando comentários completos do banco...")
        comentarios = db.get_comentarios_completos(perfil_id)
        logger.info(f"Obtidos {len(comentarios)} comentários completos")
    except Exception as e:
        logger.error(f"Erro ao buscar comentários completos: {e}", exc_info=True)
        print(f"❌ Erro ao buscar comentários: {e}")
        raise

    # Pega posts do banco
    try:
        logger.info("Buscando posts do banco...")
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

        logger.info(f"Obtidos {len(posts_do_banco)} posts do banco")
    except Exception as e:
        logger.error(f"Erro ao buscar posts do banco: {e}", exc_info=True)
        print(f"❌ Erro ao buscar posts: {e}")
        raise

    # Monta dados completos
    try:
        logger.info("Buscando dados do perfil para o relatório...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT seguidores FROM perfis WHERE id = ?", (perfil_id,))
            row = cursor.fetchone()
            seguidores = row[0] if row else 0
            logger.info(f"Seguidores do perfil: {seguidores}")
    except Exception as e:
        logger.error(f"Erro ao buscar seguidores: {e}", exc_info=True)
        seguidores = 0

    dados_completos = {
        'perfil': {
            'username': perfil_username,
            'seguidores': seguidores,
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
        logger.info("Inicializando GeradorRelatorioSheets...")
        gerador_sheets = GeradorRelatorioSheets()
        logger.info("GeradorRelatorioSheets inicializado com sucesso")

        logger.info(f"Criando relatório completo para perfil {perfil_username}...")
        logger.debug(f"Dados: {len(posts_do_banco)} posts, {len(comentarios)} comentários")

        url = gerador_sheets.criar_relatorio_completo(
            dados_completos,
            comentarios,
            resumo_analise,
            [],
            perfil_nome=perfil_username
        )

        if url:
            logger.info(f"Planilha criada com sucesso: {url}")
            print(f"✅ Planilha criada com sucesso!")
            print(f"🔗 {url}")
        else:
            logger.error("Planilha não foi criada (nenhuma URL retornada)")
            print(f"⚠️ Planilha não foi criada (erro desconhecido)")

    except FileNotFoundError as e:
        logger.error(f"Arquivo de credenciais não encontrado: {e}", exc_info=True)
        print(f"❌ Erro: Arquivo de credenciais não encontrado!")
        print(f"\n💡 Verifique:")
        print(f"   • credentials.json existe no diretório?")
        print(f"   • O caminho no config.py está correto?")
    except PermissionError as e:
        logger.error(f"Erro de permissão ao acessar Google Sheets: {e}", exc_info=True)
        print(f"❌ Erro de permissão!")
        print(f"\n💡 Verifique:")
        print(f"   • Service account tem permissão para criar planilhas?")
        print(f"   • Google Sheets API está ativada no projeto?")
    except ValueError as e:
        logger.error(f"Erro de validação ao criar planilha: {e}", exc_info=True)
        print(f"❌ Erro de validação: {e}")
        print(f"\n💡 Verifique:")
        print(f"   • credentials.json está no formato correto?")
        print(f"   • As credenciais estão válidas?")
    except Exception as e:
        logger.error(f"Erro ao gerar planilha: {e}", exc_info=True)
        print(f"❌ Erro ao gerar planilha: {e}")
        print(f"\n💡 Verifique:")
        print(f"   • credentials.json está válido?")
        print(f"   • Google Sheets API está ativada?")
        print(f"   • Service account tem permissão?")
        print(f"   • Veja o arquivo de log para mais detalhes")

    # Gera resumo executivo
    print(f"\n📄 Gerando resumo executivo...")
    logger.info("Gerando resumo executivo em TXT...")

    try:
        timestamp = datetime.now().strftime("%d-%m-%Y_%Hh%M")
        filename = f"resumo_executivo_{perfil_username.replace('@', '')}_{timestamp}.txt"
        logger.info(f"Arquivo de resumo: {filename}")

        logger.info("Buscando top usuários...")
        top_usuarios = db.get_top_usuarios(perfil_id, limit=5)
        logger.info(f"Encontrados {len(top_usuarios)} top usuários")

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

        logger.info(f"Resumo executivo salvo com sucesso: {filename}")
        print(f"✅ Resumo salvo: {filename}")

    except Exception as e:
        logger.error(f"Erro ao gerar resumo executivo: {e}", exc_info=True)
        print(f"⚠️ Erro ao gerar resumo executivo: {e}")
        # Não é crítico, apenas avisa


def main():
    banner()
    logger.info("=== INICIANDO REPROCESSAMENTO ===")

    try:
        # Inicializa banco
        logger.info(f"Inicializando banco de dados: {CONFIG['DATABASE_PATH']}")
        db = Database(CONFIG["DATABASE_PATH"])
        logger.info("Banco de dados inicializado com sucesso")

        # Lista perfis disponíveis
        perfis = listar_perfis(db)

        if not perfis:
            logger.warning("Nenhum perfil encontrado no banco")
            return

        # Escolhe perfil
        logger.info("Aguardando seleção do usuário...")
        perfil = menu_perfis(perfis)
        logger.info(f"Perfil selecionado: {perfil['username']} (ID: {perfil['id']})")

        # Reprocessa
        reprocessar_perfil(perfil['id'], perfil['username'], db)

        print(f"\n{'=' * 70}")
        print(f"✅ REPROCESSAMENTO CONCLUÍDO!")
        print(f"{'=' * 70}\n")
        logger.info("=== REPROCESSAMENTO CONCLUÍDO COM SUCESSO ===")

    except Exception as e:
        logger.critical(f"Erro fatal durante o reprocessamento: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário.\n")
        logger.warning("Processo interrompido pelo usuário (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        print(f"\n💡 Veja o arquivo de log na pasta 'logs' para mais detalhes")
        logger.critical(f"Erro fatal não tratado: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
