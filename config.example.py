# ========================================
# CONFIGURAÇÕES - EXEMPLO
# Copie para config.py e preencha!
# ========================================

CONFIG = {
    # ============ CREDENCIAIS ============
    
    "INSTAGRAM_USER": "papo.fiadobr@gmail.com",
    "INSTAGRAM_PASS": "@Jacarecoruja13",
    "OPENAI_KEY": "OPENAI_KEY": "COLE_SUA_OPENAI_KEY_AQUI",
    "GOOGLE_CREDENTIALS_FILE": "credentials.json",
    
    
    # ============ BANCO DE DADOS ============
    
    "DATABASE_PATH": "instagram_analytics.db",
    "MODO_INCREMENTAL": True,
    
    
    # ============ ANÁLISE ============
    
    "POSTS_ANALISAR": 5,
    "DELAY_ENTRE_POSTS": 45,
    "DELAY_ENTRE_COMENTARIOS": 2,
    "MODELO_GPT": "gpt-4o-mini",
    "MAX_TOKENS": 300,
    
    
    # ============ GOOGLE SHEETS ============
    
    "PLANILHA_ID": "SEU_ID_AQUI",
    "COMPARTILHAR_COM_EMAIL": "seu_email@gmail.com",
    
    
    # ============ OUTRAS CONFIGS ============
    
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
```

---

### **PASSO 3: Atualiza .gitignore**

Garante que tem isso:
```
*.db
*.pyc
__pycache__/
.env
credentials.json
config.py
*.txt
!requirements.txt
.streamlit/secrets.toml
resumo_executivo*.txt