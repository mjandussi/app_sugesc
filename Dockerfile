# ───────────────────────────────────────────────
# Dockerfile para app Streamlit - app_sugesc
# ───────────────────────────────────────────────

# Imagem base com Python 3.11
FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Define a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o app
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
