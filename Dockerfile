FROM python:3.11-slim

WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# CRÍTICO: Define variáveis de ambiente do Streamlit
# Isso SOBRESCREVE as variáveis automáticas do Railway
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expõe porta
EXPOSE 8501

# Roda Streamlit (agora vai usar as ENV acima!)
CMD ["streamlit", "run", "app.py"]
