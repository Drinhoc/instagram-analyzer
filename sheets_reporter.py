"""
GERADOR DE RELATÓRIOS - SEM ALERTAS, SEM RESUMO/PALAVRAS
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import CONFIG


class GeradorRelatorioSheets:

    def __init__(self):
        self.client = None
        self.creds = None
        self.conectar()

    def conectar(self):
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            self.creds = Credentials.from_service_account_file(
                CONFIG["GOOGLE_CREDENTIALS_FILE"],
                scopes=scopes
            )

            self.client = gspread.authorize(self.creds)
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def criar_relatorio_completo(self, dados, comentarios_analisados, resumo_analise, alertas, perfil_nome=""):

        if not self.client:
            return None

        try:
            print("\n📊 Gerando relatório no Google Sheets...")

            planilha_id = CONFIG.get("PLANILHA_ID", "")
            if not planilha_id:
                return None

            spreadsheet = self.client.open_by_key(planilha_id)

            # Limpa abas antigas deste perfil
            perfil_clean = perfil_nome.replace('@', '').replace('.', '')

            prefixos = [
                f"📊 {perfil_clean}",
                f"💬 {perfil_clean}",
                f"📸 {perfil_clean}"
            ]

            for worksheet in spreadsheet.worksheets():
                for prefixo in prefixos:
                    if worksheet.title.startswith(prefixo):
                        try:
                            spreadsheet.del_worksheet(worksheet)
                        except:
                            pass

            # Cria abas
            self._criar_aba_resumo(spreadsheet, dados, resumo_analise, perfil_clean)
            self._criar_aba_comentarios(spreadsheet, comentarios_analisados, perfil_clean)
            self._criar_aba_posts(spreadsheet, dados['posts'], perfil_clean)

            print(f"✅ Relatório atualizado!")
            return spreadsheet.url

        except Exception as e:
            print(f"❌ Erro: {e}")
            return None

    def _criar_aba_resumo(self, spreadsheet, dados, resumo, prefixo):
        try:
            titulo = f"📊 {prefixo} - Resumo"
            worksheet = spreadsheet.add_worksheet(title=titulo, rows=40, cols=10)

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

            worksheet.update(range_name='A1', values=dados_resumo)
            worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})

        except Exception as e:
            print(f"⚠️ Erro resumo: {e}")

    def _criar_aba_comentarios(self, spreadsheet, comentarios, prefixo):
        try:
            titulo = f"💬 {prefixo} - Comentários"
            worksheet = spreadsheet.add_worksheet(title=titulo, rows=len(comentarios) + 10, cols=12)

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

            worksheet.update(range_name='A1', values=dados)
            worksheet.format('A1:K1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

        except Exception as e:
            print(f"⚠️ Erro comentários: {e}")

    def _criar_aba_posts(self, spreadsheet, posts, prefixo):
        try:
            titulo = f"📸 {prefixo} - Posts"
            worksheet = spreadsheet.add_worksheet(title=titulo, rows=len(posts) + 10, cols=7)

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

            worksheet.update(range_name='A1', values=dados)
            worksheet.format('A1:F1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

        except Exception as e:
            print(f"⚠️ Erro posts: {e}")