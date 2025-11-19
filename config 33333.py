"""
Módulo responsável por carregar as configurações do projeto de forma híbrida:
1. Tenta carregar do Streamlit Secrets (Modo Nuvem)
2. Se falhar, carrega do arquivo .env (Modo Local)

O dicionário CONFIG será usado por todo o seu projeto.
"""
import os
import sys

# Tenta importar Streamlit para o modo nuvem. Se falhar, estamos no local.
try:
    import streamlit as st
except ImportError:
    st = None

from dotenv import load_dotenv

# Dicionário de configurações global
CONFIG = {}
IS_CLOUD_MODE = False

# =================================================================
# VARIÁVEIS DE AMBIENTE E SECRETS (CHAVES)
# =================================================================

# Lista de chaves simples que devem estar no .env ou no st.secrets
VARIAVEIS_SIMPLES = [
    "INSTAGRAM_USER",
    "INSTAGRAM_PASS",
    "OPENAI_KEY",
    "PLANILHA_ID",
    "PROXY_HOST",
    "PROXY_PORT",
    "PROXY_USER",
    "PROXY_PASS",
]

# Variáveis do seu projeto que têm valores fixos ou defaults
VARIAVEIS_PROJETO = {
    "DATABASE_PATH": "instagram_analytics.db",
    "GOOGLE_CREDENTIALS_FILE": "google_credentials.json", # Apenas para o modo local
    "PERFIS_ALVO": ["@doptex", "@admiravelcafe", "@descealetrashow"],
    "POSTS_ANALISAR": 20,
    "DEBUG": False,
}

# =================================================================
# LÓGICA DE CARREGAMENTO HÍBRIDO
# =================================================================

def load_config():
    """Carrega as configurações do Streamlit Secrets ou do .env."""
    global CONFIG, IS_CLOUD_MODE
    
    # 1. Modo Streamlit Cloud (st.secrets)
    if st and st.secrets:
        
        # Indica que estamos na nuvem
        IS_CLOUD_MODE = True
        
        # Carrega variáveis simples
        for var in VARIAVEIS_SIMPLES:
            CONFIG[var] = st.secrets.get(var)

        # Carrega a tabela TOML do Google Sheets
        CONFIG['GSPREAD_CREDENTIALS'] = st.secrets.get("gspread")
        
        print("✅ Configurações carregadas do Streamlit Secrets (Modo Nuvem)!")
        
    # 2. Modo Local (.env)
    else:
        
        # Carrega .env do disco
        load_dotenv()
        
        # Carrega variáveis simples
        for var in VARIAVEIS_SIMPLES:
            CONFIG[var] = os.getenv(var)
        
        # No modo local, o GSPREAD usa o arquivo.
        CONFIG['GSPREAD_CREDENTIALS'] = None # O GeradorRelatorioSheets deve buscar o arquivo
        
        print("✅ Configurações carregadas do .env (Modo Local)!")
        
    # Adiciona variáveis fixas do projeto
    CONFIG.update(VARIAVEIS_PROJETO)

    # Verifica se as variáveis críticas estão carregadas
    _check_critical_config()
    
    return CONFIG


def _check_critical_config():
    """Verifica e printa o status das configurações críticas."""
    print("\n" + "=" * 70)
    print("🔍 VALIDANDO CONFIGURAÇÕES")
    print("=" * 70)
    
    # Lista de chaves críticas para validação de print
    chaves_criticas = [
        ("INSTAGRAM_USER", "✅ INSTAGRAM_USER"),
        ("INSTAGRAM_PASS", "✅ INSTAGRAM_PASS (configurado)"),
        ("OPENAI_KEY", "✅ OPENAI_KEY (configurado)"),
        ("PLANILHA_ID", "✅ PLANILHA_ID"),
        ("PROXY_HOST", "✅ PROXY: Configurado")
    ]
    
    for key, msg in chaves_criticas:
        value = CONFIG.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            print(f"❌ {msg.replace('✅', '❌')}: FALHOU!")
            if key == "INSTAGRAM_PASS":
                # Aqui você pode interromper se uma chave crítica falhar
                print("ERRO: Configuração Crítica faltando. O script irá falhar.")
        else:
            print(f"{msg}: {value[:8]}..." if "configurado" in msg and len(value) > 8 else msg)

    # Validando Google Sheets (diferente por ambiente)
    if IS_CLOUD_MODE:
        status_sheets = "✅ GOOGLE_CREDENTIALS: OK (Streamlit Secrets)" if CONFIG.get('GSPREAD_CREDENTIALS') else "❌ GOOGLE_CREDENTIALS: FALHOU!"
    else:
        status_sheets = "✅ GOOGLE_CREDENTIALS_FILE: OK" if os.path.exists(CONFIG["GOOGLE_CREDENTIALS_FILE"]) else "⚠️ GOOGLE_CREDENTIALS_FILE: ARQUIVO LOCAL FALTANDO"
    
    print(status_sheets)

    print("=" * 70)
    print("✅ Todas as configurações OK!" if all(CONFIG.get(k[0]) for k in chaves_criticas) else "⚠️ Configurações Críticas Faltando!")

# Executa o carregamento imediatamente
load_config()

# Acessa o CONFIG (dicionário final) fora do módulo (ex: em main.py)
# from config_loader import CONFIG