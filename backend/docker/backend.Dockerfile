# D:\Projetos\DesafioTecnico\ZapSign\backend\docker\backend.Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Copiar requirements
COPY requirements.txt /app/requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar projeto
COPY . /app

# Expor porta padrão do Django
EXPOSE 8000

# Rodar collectstatic, migrações e iniciar o servidor ASGI (Daphne)
# collectstatic: Reúne arquivos CSS/JS do Admin para o WhiteNoise servir
CMD ["bash", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && daphne config.asgi:application -b 0.0.0.0 -p 8000"]