"""
CONFIG - Versão para Streamlit Cloud
Usa secrets quando disponível, senão usa valores padrão
"""

import streamlit as st

# Verifica se tá rodando no Streamlit Cloud
if hasattr(st, 'secrets'):
    CONFIG = {
        "DATABASE_PATH": "instagram_analytics.db",
        "MODO_INCREMENTAL": True,
        "INSTAGRAM_USER": st.secrets.get("INSTAGRAM_USER", ""),
        "INSTAGRAM_PASS": st.secrets.get("INSTAGRAM_PASS", ""),
        "OPENAI_KEY": st.secrets.get("OPENAI_KEY", ""),
        "GOOGLE_CREDENTIALS_FILE": "credentials.json",
        "POSTS_ANALISAR": 5,
        "DELAY_ENTRE_POSTS": 45,
        "DELAY_ENTRE_COMENTARIOS": 2,
        "MODELO_GPT": "gpt-4o-mini",
        "MAX_TOKENS": 300,
        "PLANILHA_ID": st.secrets.get("PLANILHA_ID", ""),
        "COMPARTILHAR_COM_EMAIL": "",
        "COLETAR_METRICAS_VERIFICADA": False,
        "SALVAR_JSON_BACKUP": False,
        "DIR_OUTPUT": "outputs",
        "DETECTAR_DELETADOS": True,
        "ATUALIZAR_METRICAS_POSTS": True,
        "CATEGORIAS": ["elogio", "reclamacao", "duvida", "sugestao", "spam", "outro"],
        "SENTIMENTOS": ["positivo", "neutro", "negativo"],
        "INTENTS": ["compra", "informacao", "feedback", "reclamacao", "outro"],
        "ALERTA_NEGATIVO_LIKES": 10,
        "ALERTA_SEM_RESPOSTA_HORAS": 24,
        "DEBUG": False,
    }
else:
    # Rodando localmente - carrega do config.example.py ou usa padrões
    CONFIG = {
        "DATABASE_PATH": "instagram_analytics.db",
        "MODO_INCREMENTAL": True,
        "INSTAGRAM_USER": "seu_usuario",
        "INSTAGRAM_PASS": "sua_senha",
        "OPENAI_KEY": "sua_key",
        "GOOGLE_CREDENTIALS_FILE": "credentials.json",
        "POSTS_ANALISAR": 5,
        "DELAY_ENTRE_POSTS": 45,
        "DELAY_ENTRE_COMENTARIOS": 2,
        "MODELO_GPT": "gpt-4o-mini",
        "MAX_TOKENS": 300,
        "PLANILHA_ID": "",
        "COMPARTILHAR_COM_EMAIL": "",
        "COLETAR_METRICAS_VERIFICADA": False,
        "SALVAR_JSON_BACKUP": False,
        "DIR_OUTPUT": "outputs",
        "DETECTAR_DELETADOS": True,
        "ATUALIZAR_METRICAS_POSTS": True,
        "CATEGORIAS": ["elogio", "reclamacao", "duvida", "sugestao", "spam", "outro"],
        "SENTIMENTOS": ["positivo", "neutro", "negativo"],
        "INTENTS": ["compra", "informacao", "feedback", "reclamacao", "outro"],
        "ALERTA_NEGATIVO_LIKES": 10,
        "ALERTA_SEM_RESPOSTA_HORAS": 24,
        "DEBUG": False,
    }