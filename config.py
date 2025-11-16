"""
CONFIG - Compatível com Streamlit Cloud, Railway e execução local.

Prioridade:
1) st.secrets (se existir secrets.toml — caso do Streamlit Cloud)
2) Variáveis de ambiente (Railway + execução local)
3) Valores padrão (fallback local)
"""

import os
import streamlit as st

def get_secret(key: str, default: str = "") -> str:
    """
    Tenta buscar primeiro em st.secrets (Streamlit Cloud).
    Se não existir (Railway / Local), usa variável de ambiente.
    """
    # 1) st.secrets (Streamlit Cloud)
    try:
        if hasattr(st, "secrets"):
            value = st.secrets.get(key)
            if value is not None:
                return value
    except Exception:
        pass

    # 2) Variáveis de ambiente
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    # 3) Valor padrão
    return default


CONFIG = {
    "DATABASE_PATH": "instagram_analytics.db",
    "MODO_INCREMENTAL": True,

    # Secrets
    "INSTAGRAM_USER": get_secret("INSTAGRAM_USER", ""),
    "INSTAGRAM_PASS": get_secret("INSTAGRAM_PASS", ""),
    "OPENAI_KEY": get_secret("OPENAI_KEY", ""),
    "PLANILHA_ID": get_secret("PLANILHA_ID", ""),

    # Arquivo de credenciais Google (se usar)
    "GOOGLE_CREDENTIALS_FILE": "credentials.json",

    # Configs gerais
    "POSTS_ANALISAR": 5,
    "DELAY_ENTRE_POSTS": 45,
    "DELAY_ENTRE_COMENTARIOS": 2,
    "MODELO_GPT": "gpt-4o-mini",
    "MAX_TOKENS": 300,

    # Ajustes extras
    "COMPARTILHAR_COM_EMAIL": "",
    "COLETAR_METRICAS_VERIFICADA": False,
    "SALVAR_JSON_BACKUP": False,
    "DIR_OUTPUT": "outputs",
    "DETECTAR_DELETADOS": True,
    "ATUALIZAR_METRICAS_POSTS": True,

    # Classificações
    "CATEGORIAS": ["elogio", "reclamacao", "duvida", "sugestao", "spam", "outro"],
    "SENTIMENTOS": ["positivo", "neutro", "negativo"],
    "INTENTS": ["compra", "informacao", "feedback", "reclamacao", "outro"],

    # Alertas
    "ALERTA_NEGATIVO_LIKES": 10,
    "ALERTA_SEM_RESPOSTA_HORAS": 24,

    # Debug
    "DEBUG": False,
}
