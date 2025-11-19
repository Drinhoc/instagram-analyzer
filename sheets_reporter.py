"""
GERADOR DE RELATÓRIOS - SEM ALERTAS, SEM RESUMO/PALAVRAS
"""

import gspread
import logging
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import CONFIG

logger = logging.getLogger(__name__)


class GeradorRelatorioSheets:

    def __init__(self):
        logger.info("Inicializando GeradorRelatorioSheets...")
        self.client = None
        self.creds = None
        self.conectar()

    def conectar(self):
        try:
            logger.info("Conectando ao Google Sheets API...")
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            logger.info(f"Carregando credenciais de: {CONFIG['GOOGLE_CREDENTIALS_FILE']}")
            self.creds = Credentials.from_service_account_file(
                CONFIG["GOOGLE_CREDENTIALS_FILE"],
                scopes=scopes
            )

            logger.info("Autorizando cliente gspread...")
            self.client = gspread.authorize(self.creds)
            logger.info("Cliente Google Sheets conectado com sucesso!")
            return True
        except FileNotFoundError as e:
            logger.error(f"Arquivo de credenciais não encontrado: {e}", exc_info=True)
            print(f"❌ Erro: Arquivo de credenciais não encontrado - {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao conectar com Google Sheets: {e}", exc_info=True)
            print(f"❌ Erro ao conectar: {e}")
            return False

    def criar_relatorio_completo(self, dados, comentarios_analisados, resumo_analise, alertas, perfil_nome=""):
        logger.info(f"Iniciando criação de relatório completo para perfil: {perfil_nome}")

        if not self.client:
            logger.error("Cliente Google Sheets não está conectado!")
            print("❌ Erro: Cliente não conectado ao Google Sheets")
            return None

        try:
            print("\n📊 Gerando relatório no Google Sheets...")

            planilha_id = CONFIG.get("PLANILHA_ID", "")
            logger.info(f"PLANILHA_ID do config: '{planilha_id}'")

            if not planilha_id:
                logger.error("PLANILHA_ID não está configurado no config.py!")
                print("❌ Erro: PLANILHA_ID não está configurado!")
                print("💡 Configure PLANILHA_ID no arquivo config.py ou .env")
                return None

            logger.info(f"Abrindo planilha com ID: {planilha_id}")
            spreadsheet = self.client.open_by_key(planilha_id)
            logger.info(f"Planilha aberta: {spreadsheet.title}")

            # Limpa abas antigas deste perfil
            perfil_clean = perfil_nome.replace('@', '').replace('.', '')
            logger.info(f"Perfil limpo para abas: '{perfil_clean}'")

            prefixos = [
                f"📊 {perfil_clean}",
                f"💬 {perfil_clean}",
                f"📸 {perfil_clean}"
            ]

            logger.info("Limpando abas antigas do perfil...")
            abas_removidas = 0
            for worksheet in spreadsheet.worksheets():
                for prefixo in prefixos:
                    if worksheet.title.startswith(prefixo):
                        try:
                            logger.debug(f"Removendo aba: {worksheet.title}")
                            spreadsheet.del_worksheet(worksheet)
                            abas_removidas += 1
                        except Exception as e:
                            logger.warning(f"Erro ao remover aba {worksheet.title}: {e}")

            logger.info(f"Removidas {abas_removidas} abas antigas")

            # Cria abas
            logger.info("Criando aba de resumo...")
            self._criar_aba_resumo(spreadsheet, dados, resumo_analise, perfil_clean)

            logger.info(f"Criando aba de comentários ({len(comentarios_analisados)} comentários)...")
            self._criar_aba_comentarios(spreadsheet, comentarios_analisados, perfil_clean)

            logger.info(f"Criando aba de posts ({len(dados['posts'])} posts)...")
            self._criar_aba_posts(spreadsheet, dados['posts'], perfil_clean)

            logger.info(f"Relatório criado com sucesso! URL: {spreadsheet.url}")
            print(f"✅ Relatório atualizado!")
            return spreadsheet.url

        except gspread.exceptions.APIError as e:
            logger.error(f"Erro da API do Google Sheets: {e}", exc_info=True)
            print(f"❌ Erro da API: {e}")
            print("💡 Verifique se a service account tem permissão na planilha")
            return None
        except Exception as e:
            logger.error(f"Erro ao criar relatório: {e}", exc_info=True)
            print(f"❌ Erro: {e}")
            return None

    def _criar_aba_resumo(self, spreadsheet, dados, resumo, prefixo):
        try:
            titulo = f"📊 {prefixo} - Resumo"
            logger.info(f"Criando aba de resumo: {titulo}")

            worksheet = spreadsheet.add_worksheet(title=titulo, rows=40, cols=10)
            logger.debug(f"Worksheet '{titulo}' criado")

            perfil = dados['perfil']

            dados_resumo = [
                [f"RESUMO - {perfil['username']}"],
                [""],
                ["PERFIL"],
                [f"Username: {perfil['username']}"],
                [f"Seguidores: {perfil.get('seguidores', 0):,}"],
                [f"Posts: {perfil.get('total_posts', 0)}"],
                [""],
                ["ANÁLISE"],
                [f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"],
                [f"Comentários: {resumo.get('total_comentarios', 0)}"],
                [""],
                ["SENTIMENTOS"],
            ]

            for sent, perc in resumo.get('sentimento_percentual', {}).items():
                count = resumo.get('sentimentos', {}).get(sent, 0)
                dados_resumo.append([f"{sent}: {count} ({perc}%)"])

            logger.debug(f"Atualizando dados da aba resumo ({len(dados_resumo)} linhas)...")
            worksheet.update(range_name='A1', values=dados_resumo)
            worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
            logger.info(f"Aba de resumo criada com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao criar aba de resumo: {e}", exc_info=True)
            print(f"⚠️ Erro resumo: {e}")

    def _criar_aba_comentarios(self, spreadsheet, comentarios, prefixo):
        try:
            titulo = f"💬 {prefixo} - Comentários"
            logger.info(f"Criando aba de comentários: {titulo}")

            worksheet = spreadsheet.add_worksheet(title=titulo, rows=len(comentarios) + 10, cols=12)
            logger.debug(f"Worksheet '{titulo}' criado com {len(comentarios) + 10} linhas")

            headers = [
                "Post", "Usuário", "Comentário", "Likes", "Data",
                "Sentimento", "Categoria", "Tópico", "Urgência", "Intenção", "Resposta Sugerida"
            ]

            dados = [headers]

            for c in comentarios:
                post_codigo = c.get('post_codigo', '') or (
                    c.get('post_url', '').split('/')[-2] if c.get('post_url') else '')

                dados.append([
                    post_codigo,
                    c.get('usuario', ''),
                    c.get('texto', ''),
                    c.get('likes', 0),
                    str(c.get('data_comentario', '')),
                    c.get('sentimento', ''),
                    c.get('categoria', ''),
                    c.get('topico', ''),
                    c.get('urgencia', ''),
                    c.get('intent', ''),
                    c.get('resposta_sugerida', '')
                ])

            logger.debug(f"Atualizando {len(dados)} linhas de comentários...")
            worksheet.update(range_name='A1', values=dados)
            worksheet.format('A1:K1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            logger.info(f"Aba de comentários criada com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao criar aba de comentários: {e}", exc_info=True)
            print(f"⚠️ Erro comentários: {e}")

    def _criar_aba_posts(self, spreadsheet, posts, prefixo):
        try:
            titulo = f"📸 {prefixo} - Posts"
            logger.info(f"Criando aba de posts: {titulo}")

            worksheet = spreadsheet.add_worksheet(title=titulo, rows=len(posts) + 10, cols=7)
            logger.debug(f"Worksheet '{titulo}' criado com {len(posts) + 10} linhas")

            headers = ["Código", "URL", "Likes", "Comentários", "Data", "Caption"]
            dados = [headers]

            for post in posts:
                caption = post.get('caption', '')[:100] + "..." if len(post.get('caption', '')) > 100 else post.get(
                    'caption', '')

                dados.append([
                    post.get('codigo', ''),
                    post.get('url', ''),
                    post.get('likes', 0),
                    post.get('comentarios_count', 0),
                    str(post.get('data', '')),
                    caption
                ])

            logger.debug(f"Atualizando {len(dados)} linhas de posts...")
            worksheet.update(range_name='A1', values=dados)
            worksheet.format('A1:F1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            logger.info(f"Aba de posts criada com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao criar aba de posts: {e}", exc_info=True)
            print(f"⚠️ Erro posts: {e}")