FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements simplificado para Railway
COPY requirements-railway.txt requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta (Railway usa porta dinâmica)
EXPOSE $PORT

# Comando para executar a aplicação com porta dinâmica
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 