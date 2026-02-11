# docker/django/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY ./requirements.txt /app/

# Installer dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copier l'application
COPY . /app/

# Rendre executable
RUN chmod +x /app/docker/django/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/django/entrypoint.sh"]