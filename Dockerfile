FROM python:3.11-slim

WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Variáveis de ambiente do Streamlit
# (sem travar porta fixa, quem manda na porta é o Railway)
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Porta padrão para rodar localmente (Railway ignora isso, usa PORT)
EXPOSE 8501

# Comando de start:
# - Usa a variável PORT do Railway se existir
# - Usa 8501 como padrão (pra você testar local)
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
