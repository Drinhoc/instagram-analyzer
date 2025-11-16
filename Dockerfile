FROM python:3.11-slim

WORKDIR /app

# Copia requirements primeiro
COPY requirements.txt .

# Instala dependências
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o código
COPY . .

# Torna o script executável
RUN chmod +x start.sh

# Expõe porta
EXPOSE 8501

# Usa o script de inicialização
CMD ["./start.sh"]
