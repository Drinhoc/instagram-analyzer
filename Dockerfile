# Use Python 3.11 slim
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia requirements primeiro (cache layer)
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Expõe porta (Railway usa $PORT)
EXPOSE 8501

# Comando para rodar o Streamlit
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.runOnSave=false \
    --browser.gatherUsageStats=false
