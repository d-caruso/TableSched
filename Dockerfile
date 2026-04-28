FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/ /app/backend/

RUN pip install --no-cache-dir gunicorn .

CMD ["sh", "-lc", "python manage.py migrate_schemas --shared && python manage.py migrate_schemas && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"]
