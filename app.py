"""
INTERFACE WEB DO ANALISADOR DE INSTAGRAM
Streamlit App - Versão para Railway / Cloud
"""

import streamlit as st
import sys
import os
import json
import tempfile
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Analisador Instagram",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURAÇÃO - USA CONFIG (secrets/env) SEM DEPENDER DE secrets.toml
# ============================================================================

from config import CONFIG

def setup_google_credentials():
    """
    Configura GOOGLE_CREDENTIALS_FILE a partir de:
    1) st.secrets["google_credentials"] (se existir, caso Streamlit Cloud)
    2) Variável de ambiente GOOGLE_CREDENTIALS_JSON (JSON inteiro em string)
    3) Caso nada exista, não faz nada (e o app continua rodando)
    """
    try:
        credentials_data = None

        # 1) Streamlit Cloud: st.secrets
        try:
            if hasattr(st, "secrets") and "google_credentials" in st.secrets:
                credentials_data = dict(st.secrets["google_credentials"])
        except Exception:
            pass

        # 2) Railway/local: variável de ambiente
        if credentials_data is None:
            creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if creds_json:
                credentials_data = json.loads(creds_json)

        # 3) Se não tiver credencial nenhuma, só sai
        if not credentials_data:
            return

        # Cria arquivo temporário com as credenciais
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(credentials_data, f)
            CONFIG["GOOGLE_CREDENTIALS_FILE"] = f.name

    except Exception:
        # Não queremos que falha de credencial derrube o app inteiro
        pass


# Chama a configuração opcional das credenciais Google
setup_google_credentials()

# Importa módulos
from database import Database
from analisador import AnalisadorGPT
from sheets_reporter import GeradorRelatorioSheets

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #E1306C;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #E1306C;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #C13584;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📊 Analisador de Instagram</div>', unsafe_allow_html=True)
st.markdown("### Análise inteligente de comentários com GPT-4 💬✨")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    # Verifica credenciais (vindas do CONFIG)
    creds_ok = (
        CONFIG.get("INSTAGRAM_USER")
        and CONFIG.get("INSTAGRAM_PASS")
        and CONFIG.get("OPENAI_KEY")
        and CONFIG.get("PLANILHA_ID")
    )

    if creds_ok:
        st.success("✅ Credenciais configuradas!")
    else:
        st.error("❌ Configure as credenciais nas variáveis de ambiente / secrets!")
        st.info("No Railway: Settings → Variables")
        st.stop()

    st.markdown("---")
    st.markdown("### 📊 Sobre")
    st.info("""
    Sistema de análise automática de comentários do Instagram usando GPT-4.

    **Recursos:**
    - Análise de sentimentos
    - Categorização automática
    - Detecção de urgências
    - Relatório em Google Sheets
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["🎯 Análise Rápida", "📈 Histórico", "🔍 Diagnóstico"])

with tab1:
    st.markdown("## 🎯 Análise Rápida")
    st.markdown("Digite os perfis do Instagram que deseja analisar:")

    col1, col2 = st.columns([3, 1])

    with col1:
        perfis_input = st.text_area(
            "Perfis do Instagram",
            placeholder="@admiravelcafe\n@outroperfil\n@maisperfis",
            height=150,
            help="Digite um perfil por linha. Pode usar ou não o @"
        )

    with col2:
        num_posts = st.number_input(
            "Nº de Posts",
            min_value=1,
            max_value=50,
            value=5,
            help="Quantos posts recentes analisar"
        )

        st.markdown("###")
        analisar_btn = st.button("🚀 ANALISAR", key="analisar_rapido", use_container_width=True)

    if analisar_btn:
        # Processa perfis
        perfis = [p.strip() for p in perfis_input.split('\n') if p.strip()]

        if not perfis:
            st.error("❌ Digite pelo menos um perfil!")
            st.stop()

        # Garante @ no início
        perfis = ['@' + p.replace('@', '') for p in perfis]

        st.markdown("---")
        st.markdown(f"### 📊 Analisando {len(perfis)} perfil(s)...")

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Inicializa componentes
        try:
            CONFIG['POSTS_ANALISAR'] = num_posts

            db = Database(CONFIG["DATABASE_PATH"])

            status_text.text("🔐 Fazendo login no Instagram...")

            # ============================================================================
            # DEBUG: Mostra info de configuração (sem expor credenciais completas)
            # ============================================================================
            with st.expander("🔍 Informações de Configuração", expanded=False):
                username = str(CONFIG.get("INSTAGRAM_USER", "")).strip()
                password = str(CONFIG.get("INSTAGRAM_PASS", "")).strip()
                proxy_host = CONFIG.get("PROXY_HOST", "")
                proxy_port = CONFIG.get("PROXY_PORT", "")

                st.write("**Credenciais Instagram:**")
                st.write(f"• Username: {username[:5]}...{username[-5:] if len(username) > 10 else ''} ({len(username)} chars)")
                st.write(f"• Password: {'*' * min(len(password), 10)} ({len(password)} chars)")

                st.write("\n**Proxy:**")
                if proxy_host and proxy_port:
                    st.write(f"• ✅ Configurado: {proxy_host}:{proxy_port}")
                else:
                    st.write("• ❌ NÃO configurado!")

                st.write("\n**Ambiente:**")
                st.write(f"• Streamlit version: {st.__version__}")
                st.write(f"• Python version: {sys.version.split()[0]}")

            # Login do Instagram COM PROXY (usa ColetorInstagram!)
            from coletor import ColetorInstagram
            import logging

            # Captura logs do coletor para mostrar no Streamlit
            log_container = st.empty()

            try:
                # Mostra info de proxy
                if CONFIG.get("PROXY_HOST"):
                    st.success(f"🌐 Proxy configurado: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")
                else:
                    st.error("❌ PROXY NÃO CONFIGURADO!")
                    st.error("⚠️ No Streamlit Cloud, login SEM proxy provavelmente falhará!")
                    st.info("💡 Configure PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS no Streamlit Secrets")
                    st.stop()

                username = str(CONFIG.get("INSTAGRAM_USER", "")).strip()
                password = str(CONFIG.get("INSTAGRAM_PASS", "")).strip()

                if not username or not password:
                    st.error("❌ Credenciais Instagram vazias!")
                    st.error(f"Username: {len(username)} chars, Password: {len(password)} chars")
                    st.info("💡 Verifique se INSTAGRAM_USER e INSTAGRAM_PASS estão configurados no Streamlit Secrets")
                    st.stop()

                log_container.info("🔄 Inicializando cliente Instagram...")
                coletor_temp = ColetorInstagram()

                log_container.info(f"🔑 Tentando login como {username[:10]}...")

                # Usa o método fazer_login da classe ColetorInstagram
                # Agora lança exceção se falhar (em vez de retornar False)
                coletor_temp.fazer_login(username, password)

                # Login OK! Usa o client configurado
                coletor_client = coletor_temp.client
                log_container.success("✅ Login realizado com sucesso!")
                status_text.text("✅ Login realizado com sucesso!")

            except Exception as e:
                st.error("❌ ERRO CRÍTICO no login do Instagram!")
                st.error(f"**Tipo do erro:** {type(e).__name__}")
                st.error(f"**Mensagem:** {str(e)}")

                # Analisa o erro e dá dicas específicas
                erro_str = str(e).lower()

                st.markdown("### 💡 Diagnóstico:")

                if "checkpoint" in erro_str or "challenge" in erro_str:
                    st.warning("🚨 **Conta com checkpoint/desafio de segurança**")
                    st.info("Acesse instagram.com pelo navegador e resolva a verificação")

                elif "login" in erro_str or "password" in erro_str:
                    st.warning("🔑 **Erro de autenticação**")
                    st.info("Verifique se as credenciais estão corretas no Streamlit Secrets")

                elif "proxy" in erro_str or "connection" in erro_str:
                    st.warning("🌐 **Erro de conexão/proxy**")
                    st.info("Verifique se o proxy está configurado corretamente")
                    st.info("Formato esperado: host=p.webshare.io, port=80, user=xxxx, pass=xxxx")

                elif "ip" in erro_str or "block" in erro_str or "spam" in erro_str:
                    st.warning("🚫 **IP bloqueado pelo Instagram**")
                    st.error("Instagram bloqueou o IP do Streamlit Cloud!")
                    st.success("✅ **SOLUÇÃO:** Configure proxy residencial no Streamlit Secrets")

                elif "timeout" in erro_str:
                    st.warning("⏱️ **Timeout de conexão**")
                    st.info("Instagram demorou demais para responder. Tente novamente.")

                else:
                    st.warning("❓ **Erro desconhecido**")
                    st.info("Veja o traceback completo abaixo")

                with st.expander("🐛 Traceback completo (para debug)"):
                    import traceback
                    st.code(traceback.format_exc())

                with st.expander("🔍 Informações do ambiente"):
                    st.write(f"Username length: {len(username) if username else 0}")
                    st.write(f"Password length: {len(password) if password else 0}")
                    st.write(f"Proxy configurado: {bool(CONFIG.get('PROXY_HOST'))}")
                    st.write(f"PROXY_HOST: {CONFIG.get('PROXY_HOST', 'NÃO CONFIGURADO')}")
                    st.write(f"PROXY_PORT: {CONFIG.get('PROXY_PORT', 'NÃO CONFIGURADO')}")
                    st.write(f"Streamlit version: {st.__version__}")
                    st.write(f"Python version: {sys.version}")

                st.stop()

            # Função auxiliar para coletar
            def coletar_perfil(perfil, num_posts):
                from coletor import ColetorInstagram
                temp_coletor = ColetorInstagram()
                temp_coletor.client = coletor_client
                return temp_coletor.coletar_tudo(perfil, num_posts)

            analisador = AnalisadorGPT()
            gerador_sheets = GeradorRelatorioSheets()

            resultados = []

            for idx, perfil in enumerate(perfis):
                progress = (idx) / len(perfis)
                progress_bar.progress(progress)
                status_text.text(f"📊 Analisando {perfil}... ({idx + 1}/{len(perfis)})")

                # Coleta dados
                with st.expander(f"📸 {perfil} - Log detalhado", expanded=False):
                    st.write(f"🎯 Coletando dados de {perfil}...")

                    perfil_existente = db.buscar_perfil(perfil)

                    if perfil_existente:
                        st.info("✅ Perfil encontrado no banco")
                        perfil_id = perfil_existente['id']
                    else:
                        st.info("🆕 Perfil novo! Primeira análise.")
                        perfil_id = None

                    # Coleta
                    dados = coletar_perfil(perfil, num_posts)
                    perfil_id = db.inserir_perfil(dados['perfil'])

                    st.write(f"✅ {len(dados['posts'])} posts coletados")

                    # Salva comentários
                    total_comentarios = 0
                    for post in dados['posts']:
                        post_id = db.inserir_post(perfil_id, post)
                        for comentario in post['comentarios']:
                            db.inserir_comentario(post_id, comentario)
                            total_comentarios += 1

                    st.write(f"✅ {total_comentarios} comentários salvos")

                    # Analisa
                    comentarios_pendentes = db.buscar_comentarios_nao_analisados(perfil_id)

                    if comentarios_pendentes:
                        st.write(f"🤖 Analisando {len(comentarios_pendentes)} comentários...")

                        analise_progress = st.progress(0)
                        for i, comentario in enumerate(comentarios_pendentes):
                            analise = analisador.analisar_comentario(comentario['texto'])
                            db.inserir_analise(comentario['id'], analise, 0.0)
                            analise_progress.progress((i + 1) / len(comentarios_pendentes))

                        st.success(f"✅ Análises concluídas! Custo: ${analisador.custo_estimado:.4f}")
                    else:
                        st.success("✅ Nenhum comentário novo!")

                # Gera planilha
                comentarios = db.get_comentarios_completos(perfil_id)
                stats = db.get_estatisticas_gerais(perfil_id)

                # Pega posts
                posts_do_banco = []
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT post_id, codigo, url, tipo, likes, comentarios_count, data_post, caption
                        FROM posts WHERE perfil_id = ?
                        ORDER BY data_post DESC
                    """, (perfil_id,))

                    for row in cursor.fetchall():
                        posts_do_banco.append({
                            'id': row[0], 'codigo': row[1], 'url': row[2],
                            'tipo': row[3], 'likes': row[4], 'comentarios_count': row[5],
                            'data': row[6], 'caption': row[7]
                        })

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
                }

                total = len(comentarios) or 1
                for sent, count in stats.get('sentimentos', {}).items():
                    resumo_analise['sentimento_percentual'][sent] = round(count / total * 100, 1)

                url = gerador_sheets.criar_relatorio_completo(
                    dados_completos, comentarios, resumo_analise, [], perfil_nome=perfil
                )

                resultados.append({
                    'perfil': perfil,
                    'comentarios': len(comentarios),
                    'posts': len(posts_do_banco),
                    'url': url,
                    'sentimentos': stats.get('sentimentos', {})
                })

            progress_bar.progress(1.0)
            status_text.text("✅ Análise concluída!")

            # Resultados
            st.markdown("---")
            st.markdown("## 🎉 Análise Concluída!")

            for resultado in resultados:
                with st.container():
                    st.markdown(f"### {resultado['perfil']}")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("📸 Posts", resultado['posts'])
                    col2.metric("💬 Comentários", resultado['comentarios'])

                    # Sentimento predominante
                    sentimentos = resultado['sentimentos']
                    if sentimentos:
                        predominante = max(sentimentos, key=sentimentos.get)
                        emoji = "😊" if predominante == "positivo" else "😐" if predominante == "neutro" else "😞"
                        col3.metric(f"{emoji} Sentimento", predominante.capitalize())

                    if resultado['url']:
                        st.link_button(
                            "📊 Abrir Google Sheets",
                            resultado['url'],
                            use_container_width=True
                        )

                    st.markdown("---")

            st.balloons()

        except Exception as e:
            st.error(f"❌ Erro durante análise: {str(e)}")
            import traceback
            with st.expander("Ver detalhes do erro"):
                st.code(traceback.format_exc())

with tab2:
    st.markdown("## 📈 Histórico de Análises")

    try:
        db = Database(CONFIG["DATABASE_PATH"])

        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, seguidores, total_posts, data_ultima_atualizacao
                FROM perfis
                ORDER BY data_ultima_atualizacao DESC
            """)

            perfis_historico = cursor.fetchall()

        if perfis_historico:
            st.markdown(f"### 📊 {len(perfis_historico)} perfil(s) no banco")

            for perfil in perfis_historico:
                with st.expander(f"📸 {perfil[0]}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Seguidores", f"{perfil[1]:,}")
                    col2.metric("Posts", perfil[2])
                    col3.metric("Última análise", perfil[3])
        else:
            st.info("📭 Nenhuma análise realizada ainda!")

    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar histórico: {str(e)}")

with tab3:
    from pagina_diagnostico import pagina_diagnostico
    pagina_diagnostico()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    Feito com ❤️ para análise de Instagram<br>
    Powered by GPT-4 & Streamlit
</div>
""", unsafe_allow_html=True)
