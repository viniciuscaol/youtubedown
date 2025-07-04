# Usar uma imagem slim do Python, bem mais leve
FROM python:3.11-slim

# Definir o diretório de trabalho
WORKDIR /app

# Instalar ffmpeg, que continua sendo necessário
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de dependências
COPY requirements.txt .

# Instalar as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os arquivos da aplicação (app.py, pastas static e templates)
COPY . .

# Criar o diretório de downloads dentro do container
RUN mkdir /downloads

# Expor a porta que o Flask usará
EXPOSE 5000

# Comando para iniciar o servidor Flask
# O host 0.0.0.0 é essencial para que seja acessível de fora do container
CMD ["flask", "run", "--host=0.0.0.0"]