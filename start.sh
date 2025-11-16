#!/bin/bash

# Script de inicialização do Streamlit
# Garante que a variável $PORT seja expandida corretamente

# Define porta padrão se não existir
PORT=${PORT:-8501}

echo "🚀 Iniciando Streamlit na porta $PORT..."

# Executa Streamlit
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.runOnSave=false \
    --browser.gatherUsageStats=false
