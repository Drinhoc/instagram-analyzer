"""
Configurações centralizadas do sistema
Suporta: Local, Streamlit Cloud com PROXY RESIDENCIAL
"""

import os
import json
import tempfile

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
}

# ============================================================================
# STREAMLIT CLOUD: Carrega do st.secrets
# ============================================================================
try:
    import streamlit as st
    
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
    
    # Google Credentials
    if "google_credentials" in st.secrets:
        credentials_data = dict(st.secrets["google_credentials"])
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_data, f)
            CONFIG["GOOGLE_CREDENTIALS_FILE"] = f.name
        print("✅ Google Credentials carregados do Streamlit!")

except ImportError:
    # Não tá no Streamlit, tudo bem!
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
    obrigatorias = [
        "INSTAGRAM_USER",
        "INSTAGRAM_PASS", 
        "OPENAI_KEY",
        "PLANILHA_ID"
    ]
    
    faltando = []
    for key in obrigatorias:
        if not CONFIG.get(key):
            faltando.append(key)
    
    if faltando:
        print(f"⚠️ Configurações faltando: {', '.join(faltando)}")
        return False
    
    if not os.path.exists(CONFIG["GOOGLE_CREDENTIALS_FILE"]):
        print(f"⚠️ Arquivo {CONFIG['GOOGLE_CREDENTIALS_FILE']} não encontrado!")
        return False
    
    # Verifica proxy
    if get_proxy_dict():
        print("✅ Proxy configurado!")
    else:
        print("⚠️ Proxy NÃO configurado (opcional mas recomendado)")
    
    return True

# Validação automática ao importar
if __name__ != "__main__":
    if validar_config():
        print("✅ Todas as configurações OK!")
    else:
        print("❌ Erro nas configurações!")
