#!/bin/sh
# Загружает все начальные данные в пустую БД.
# Запускать ПОСЛЕ первого `docker compose up -d`.
# Использование: docker compose exec web sh /app/docker/init_data.sh

set -e

cd /app/src

echo "==> Загрузка офиса..."
python manage.py loaddata apps/contacts/fixtures/initial_office.json

echo "==> Загрузка фондов..."
python manage.py loaddata apps/holdings/fixtures/initial_funds.json

echo "==> Загрузка команды..."
python manage.py loaddata apps/core/fixtures/initial_team.json

echo ""
echo "Готово. Все начальные данные загружены."
echo "Следующий шаг: docker compose exec web python manage.py createsuperuser"
