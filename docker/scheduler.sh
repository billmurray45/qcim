#!/bin/sh
set -e

echo "Waiting for postgres..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
    sleep 2
done

# Write crontab: fetch news every day at 08:00 UTC
echo "0 8 * * * root cd /app/src && python manage.py fetch_external_news --limit 10 >> /app/var/logs/scheduler.log 2>&1" \
    > /etc/cron.d/fetch-news

chmod 0644 /etc/cron.d/fetch-news
touch /app/var/logs/scheduler.log

echo "Scheduler started. Next run: daily at 08:00 UTC."
exec cron -f
