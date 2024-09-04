# Dockerfile para Flask
FROM python:3.9-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código
COPY app/ ./

# Defina a variável de ambiente para a aplicação Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Exponha a porta que a aplicação Flask usará
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["flask", "run"]