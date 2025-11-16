# Use Python 3.11 slim
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Atualiza PATH para incluir binários do Python
ENV PATH="/usr/local/bin:${PATH}"

# Copia requirements primeiro (cache layer)
COPY requirements.txt .

# Atualiza pip e instala dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Expõe porta (Railway usa $PORT)
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health || exit 1

# Comando para rodar o Streamlit (usando python -m)
CMD python -m streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.runOnSave=false \
    --browser.gatherUsageStats=false