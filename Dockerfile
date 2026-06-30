FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    cron \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src

RUN SECRET_KEY=build-time-placeholder python manage.py compilemessages --verbosity 0

RUN mkdir -p /app/var/staticfiles /app/var/media /app/var/logs

EXPOSE 8000
