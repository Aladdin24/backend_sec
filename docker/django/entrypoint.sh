#!/bin/bash
# docker/django/entrypoint.sh

# Attendre que PostgreSQL soit prêt (optionnel si tu veux le garder)
# while ! nc -z db 5432; do
#   sleep 1
# done

# Collecter les static files (si besoin)
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

# Lancer le serveur
exec gunicorn --bind 0.0.0.0:8000 secure_doc.wsgi:application