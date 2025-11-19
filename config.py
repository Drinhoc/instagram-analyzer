"""
Configurações centralizadas do sistema
Suporta: Local (.env), Streamlit Cloud (secrets) com PROXY RESIDENCIAL
Versão 2.3 - Suporte a .env local
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Fix encoding no Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# ============================================================================
# CARREGA .ENV SE EXISTIR (USO LOCAL)
# ============================================================================
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Arquivo .env carregado (modo local)")
except ImportError:
    # dotenv não instalado, tudo bem (Streamlit Cloud não precisa)
    pass

# Configurações padrão
CONFIG = {
    # Instagram
    "INSTAGRAM_USER": os.getenv("INSTAGRAM_USER", ""),
    "INSTAGRAM_PASS": os.getenv("INSTAGRAM_PASS", ""),
    
    # OpenAI
    "OPENAI_KEY": os.getenv("OPENAI_KEY", ""),
    
    # Google Sheets
    "PLANILHA_ID": os.getenv("PLANILHA_ID", ""),
    
    # PROXY RESIDENCIAL (NOVO!)
    "PROXY_HOST": os.getenv("PROXY_HOST", ""),  # Ex: p.webshare.io
    "PROXY_PORT": os.getenv("PROXY_PORT", ""),  # Ex: 80
    "PROXY_USER": os.getenv("PROXY_USER", ""),  # Ex: meuuser-rotate
    "PROXY_PASS": os.getenv("PROXY_PASS", ""),  # Ex: minhasenha123
    
    # Google Credentials
    "GOOGLE_CREDENTIALS_FILE": "credentials.json",
    
    # Database
    "DATABASE_PATH": "instagram_analytics.db",

    # Coleta
    "POSTS_ANALISAR": 5,
    "MAX_COMENTARIOS_POR_POST": 100,

    # Análise GPT
    "MODELO_GPT": "gpt-4o-mini",
    "MAX_TOKENS": 300,
}

# ============================================================================
# STREAMLIT CLOUD: Carrega do st.secrets
# ============================================================================
try:
    import streamlit as st

    print("🔧 Carregando configurações do Streamlit Cloud...")

    # Atualiza configs do Streamlit
    CONFIG["INSTAGRAM_USER"] = st.secrets.get("INSTAGRAM_USER", CONFIG["INSTAGRAM_USER"])
    CONFIG["INSTAGRAM_PASS"] = st.secrets.get("INSTAGRAM_PASS", CONFIG["INSTAGRAM_PASS"])
    CONFIG["OPENAI_KEY"] = st.secrets.get("OPENAI_KEY", CONFIG["OPENAI_KEY"])
    CONFIG["PLANILHA_ID"] = st.secrets.get("PLANILHA_ID", CONFIG["PLANILHA_ID"])

    # PROXY (NOVO!)
    CONFIG["PROXY_HOST"] = st.secrets.get("PROXY_HOST", CONFIG["PROXY_HOST"])
    CONFIG["PROXY_PORT"] = st.secrets.get("PROXY_PORT", CONFIG["PROXY_PORT"])
    CONFIG["PROXY_USER"] = st.secrets.get("PROXY_USER", CONFIG["PROXY_USER"])
    CONFIG["PROXY_PASS"] = st.secrets.get("PROXY_PASS", CONFIG["PROXY_PASS"])

    # Debug de proxy
    if CONFIG["PROXY_HOST"]:
        print(f"✅ Proxy carregado: {CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}")
    else:
        print("⚠️ Nenhum proxy configurado nos secrets!")

    # Google Credentials
    if "google_credentials" in st.secrets:
        credentials_data = dict(st.secrets["google_credentials"])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_data, f)
            CONFIG["GOOGLE_CREDENTIALS_FILE"] = f.name
        print("✅ Google Credentials carregados do Streamlit!")

    print("✅ Configurações do Streamlit carregadas com sucesso!")

except ImportError:
    # Não tá no Streamlit, rodando local
    print("Rodando local (nao e Streamlit Cloud)")
    pass

# ============================================================================
# HELPER: Monta URL do proxy
# ============================================================================
def get_proxy_dict():
    """Retorna dict de proxy formatado para requests/instagrapi"""
    if not all([CONFIG["PROXY_HOST"], CONFIG["PROXY_PORT"], 
                CONFIG["PROXY_USER"], CONFIG["PROXY_PASS"]]):
        return None
    
    proxy_url = f"http://{CONFIG['PROXY_USER']}:{CONFIG['PROXY_PASS']}@{CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']}"
    
    return {
        "http": proxy_url,
        "https": proxy_url
    }

# ============================================================================
# VALIDAÇÃO
# ============================================================================
def validar_config():
    """Valida se todas as configurações necessárias estão presentes"""
    print("\n" + "=" * 70)
    print("🔍 VALIDANDO CONFIGURAÇÕES")
    print("=" * 70)

    obrigatorias = [
        "INSTAGRAM_USER",
        "INSTAGRAM_PASS",
        "OPENAI_KEY",
        "PLANILHA_ID"
    ]

    faltando = []
    for key in obrigatorias:
        valor = CONFIG.get(key)
        if not valor:
            faltando.append(key)
            print(f"❌ {key}: FALTANDO")
        else:
            # Mostra parcialmente para debug (sem expor credenciais completas)
            if "PASS" in key or "KEY" in key:
                print(f"✅ {key}: {'*' * 10} (configurado)")
            else:
                print(f"✅ {key}: {valor}")

    if faltando:
        print(f"\n⚠️ Configurações faltando: {', '.join(faltando)}")
        print("=" * 70 + "\n")
        return False

    # Verifica Google Credentials
    if not os.path.exists(CONFIG["GOOGLE_CREDENTIALS_FILE"]):
        print(f"❌ GOOGLE_CREDENTIALS_FILE: Arquivo não encontrado!")
        print(f"   Caminho: {CONFIG['GOOGLE_CREDENTIALS_FILE']}")
        print("=" * 70 + "\n")
        return False
    else:
        print(f"✅ GOOGLE_CREDENTIALS_FILE: OK")

    # Verifica proxy (IMPORTANTE!)
    proxy_dict = get_proxy_dict()
    if proxy_dict:
        print(f"✅ PROXY: Configurado ({CONFIG['PROXY_HOST']}:{CONFIG['PROXY_PORT']})")
    else:
        print("⚠️ PROXY: NÃO configurado")
        print("   ⚠️ ATENÇÃO: Sem proxy, o Instagram pode bloquear seu IP!")
        print("   💡 Configure PROXY_HOST, PROXY_PORT, PROXY_USER e PROXY_PASS")

    print("=" * 70 + "\n")
    return True

# Validação automática ao importar
if __name__ != "__main__":
    if validar_config():
        print("✅ Todas as configurações OK!")
    else:
        print("❌ Erro nas configurações!")
