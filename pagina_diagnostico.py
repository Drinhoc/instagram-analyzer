"""
PÁGINA DE DIAGNÓSTICO STREAMLIT
Adicione isso como uma aba no app.py para debugar
"""

import streamlit as st
import requests
from config import CONFIG

def pagina_diagnostico():
    """Página de diagnóstico completa"""

    st.markdown("## 🔍 DIAGNÓSTICO COMPLETO")

    # ============================================================================
    # TESTE 1: Configurações
    # ============================================================================
    with st.expander("✅ TESTE 1: Configurações", expanded=True):
        st.markdown("### Variáveis carregadas:")

        configs_check = {
            "INSTAGRAM_USER": CONFIG.get("INSTAGRAM_USER", ""),
            "INSTAGRAM_PASS": "***" if CONFIG.get("INSTAGRAM_PASS") else "",
            "OPENAI_KEY": "***" if CONFIG.get("OPENAI_KEY") else "",
            "PLANILHA_ID": CONFIG.get("PLANILHA_ID", ""),
            "PROXY_HOST": CONFIG.get("PROXY_HOST", ""),
            "PROXY_PORT": CONFIG.get("PROXY_PORT", ""),
            "PROXY_USER": CONFIG.get("PROXY_USER", ""),
            "PROXY_PASS": "***" if CONFIG.get("PROXY_PASS") else "",
        }

        for key, value in configs_check.items():
            if value:
                st.success(f"✅ {key}: {value}")
            else:
                st.error(f"❌ {key}: NÃO CONFIGURADO")

    # ============================================================================
    # TESTE 2: IP Público
    # ============================================================================
    with st.expander("🌐 TESTE 2: IP Público (SEM proxy)", expanded=True):
        try:
            ip = requests.get("https://api.ipify.org", timeout=10).text
            st.success(f"✅ Seu IP público: **{ip}**")
            st.info("Este é o IP que o Streamlit Cloud está usando")
        except Exception as e:
            st.error(f"❌ Erro ao buscar IP: {e}")

    # ============================================================================
    # TESTE 3: Proxy
    # ============================================================================
    with st.expander("🔐 TESTE 3: Testando Proxy", expanded=True):
        if not all([CONFIG.get("PROXY_HOST"), CONFIG.get("PROXY_PORT"),
                    CONFIG.get("PROXY_USER"), CONFIG.get("PROXY_PASS")]):
            st.error("❌ Proxy NÃO configurado!")
            st.stop()

        st.info(f"Proxy configurado: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")

        # Monta URL do proxy
        proxy_url = f"http://{CONFIG['PROXY_USER']}:{CONFIG['PROXY_PASS']}@{CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}"
        proxy_dict = {
            "http": proxy_url,
            "https": proxy_url
        }

        st.write("🔄 Testando conexão COM proxy...")

        try:
            ip_com_proxy = requests.get("https://api.ipify.org", proxies=proxy_dict, timeout=15).text
            st.success(f"✅ IP COM proxy: **{ip_com_proxy}**")

            # Compara IPs
            try:
                ip_sem_proxy = requests.get("https://api.ipify.org", timeout=10).text
                if ip_sem_proxy != ip_com_proxy:
                    st.success("✅ PROXY FUNCIONANDO! IPs são diferentes!")
                else:
                    st.warning("⚠️ IPs iguais! Proxy pode não estar funcionando!")
            except:
                pass

        except Exception as e:
            st.error(f"❌ ERRO ao usar proxy: {e}")
            st.error("💡 O Streamlit Cloud pode estar BLOQUEANDO conexões via proxy!")
            st.info("Isso explicaria por que funciona local mas falha no cloud.")

    # ============================================================================
    # TESTE 4: Instagram (importação)
    # ============================================================================
    with st.expander("📸 TESTE 4: Importando módulos Instagram", expanded=True):
        try:
            from instagrapi import Client
            st.success("✅ instagrapi importado com sucesso!")

            from coletor import ColetorInstagram
            st.success("✅ ColetorInstagram importado com sucesso!")

        except Exception as e:
            st.error(f"❌ Erro ao importar: {e}")

    # ============================================================================
    # TESTE 5: Login Instagram
    # ============================================================================
    with st.expander("🔐 TESTE 5: Tentativa de Login Instagram", expanded=False):
        st.warning("⚠️ Este teste vai tentar fazer login no Instagram!")

        if st.button("▶️ TESTAR LOGIN"):
            try:
                from coletor import ColetorInstagram

                with st.spinner("🔄 Inicializando coletor..."):
                    coletor = ColetorInstagram()

                with st.spinner("🔐 Fazendo login..."):
                    coletor.fazer_login()

                st.success("✅ LOGIN FUNCIONOU!!!")
                st.balloons()

            except Exception as e:
                st.error(f"❌ ERRO NO LOGIN: {e}")
                st.error(f"**Tipo:** {type(e).__name__}")

                erro_str = str(e)

                if "CHALLENGE_REQUIRED" in erro_str or "CHECKPOINT" in erro_str:
                    st.warning("🚨 Conta com checkpoint/verificação")
                    st.info("Resolva em instagram.com")

                elif "IP_BLOCKED" in erro_str:
                    st.warning("🚫 IP bloqueado")
                    st.info("Possível que Streamlit Cloud esteja bloqueando proxy")

                elif "BAD_CREDENTIALS" in erro_str:
                    st.warning("🔑 Credenciais incorretas")

                else:
                    st.warning("❓ Erro desconhecido - veja detalhes acima")

    # ============================================================================
    # DIAGNÓSTICO FINAL
    # ============================================================================
    st.markdown("---")
    st.markdown("### 💡 Próximos passos:")

    st.markdown("""
    1. **Se proxy NÃO funcionou (IPs iguais ou erro):**
       - Streamlit Cloud pode estar bloqueando proxies
       - Tente usar outro serviço de deploy (Railway, Render, etc)

    2. **Se proxy funcionou MAS login falhou:**
       - Veja o tipo de erro específico no Teste 5
       - Pode ser checkpoint, credenciais, 2FA, etc

    3. **Se TUDO funcionou:**
       - Parabéns! Pode usar o app normalmente! 🎉
    """)
