# Dockerfile para Flask
FROM python:3.9-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copie o restante do código
COPY . .

# Exponha a porta que a aplicação Flask usará
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python", "run.py"]