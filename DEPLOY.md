# Инструкция по деплою — qicm.kz

## Требования к серверу

- Ubuntu 22.04 / Debian 12
- Минимум 2 GB RAM, 20 GB диск
- Открытые порты: 22, 80, 443
- DNS: `qicm.kz` и `www.qicm.kz` указывают на IP сервера

---

## 1. Подготовка сервера

```bash
# Обновить систему
apt update && apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Установить Docker Compose plugin
apt install -y docker-compose-plugin

# Проверить
docker --version
docker compose version
```

---

## 2. Создать пользователя (не работать под root)

```bash
adduser deploy
usermod -aG docker deploy
su - deploy
```

---

## 3. Загрузить код на сервер

```bash
# Вариант A: git clone
git clone https://github.com/your-org/tender-design.git /home/deploy/app
cd /home/deploy/app

# Вариант B: scp с локальной машины
scp -r /home/bauka45/myprojects/tender-design deploy@SERVER_IP:/home/deploy/app
```

---

## 4. Создать .env файл

```bash
cd /home/deploy/app
cp .env.example .env
nano .env
```

Заполнить все значения:

```env
# Генерировать новый ключ:
# python3 -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=сгенерированный-ключ

DEBUG=False

ALLOWED_HOSTS=qicm.kz,www.qicm.kz
CSRF_TRUSTED_ORIGINS=https://qicm.kz,https://www.qicm.kz

DB_USER=invest_admin
DB_PASSWORD=сильный-пароль-минимум-20-символов
DB_NAME=invest_db
DB_PORT=5432
DB_HOST=localhost

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=app-password-из-google
DEFAULT_FROM_EMAIL=noreply@qicm.kz
SERVER_EMAIL=noreply@qicm.kz

CONTACT_EMAIL_RECIPIENTS=admin@qicm.kz
```

```bash
# Ограничить права на .env
chmod 600 .env
```

---

## 5. Получить SSL-сертификат (первый раз)

Проблема: nginx не стартует без сертификата, certbot не работает без nginx.  
Решение: временно запустить nginx только с HTTP блоком.

### Шаг 5.1 — временный nginx.conf только для HTTP

```bash
cat > docker/nginx/nginx-bootstrap.conf << 'EOF'
server {
    listen 80;
    server_name qicm.kz www.qicm.kz;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'ok';
        add_header Content-Type text/plain;
    }
}
EOF

# Временно использовать bootstrap конфиг
cp docker/nginx/nginx.conf docker/nginx/nginx.conf.prod
cp docker/nginx/nginx-bootstrap.conf docker/nginx/nginx.conf
```

### Шаг 5.2 — поднять только nginx и certbot volumes

```bash
docker compose up -d nginx
```

### Шаг 5.3 — получить сертификат

```bash
docker compose run --rm certbot certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  -d qicm.kz \
  -d www.qicm.kz \
  --email admin@qicm.kz \
  --agree-tos \
  --no-eff-email
```

Ожидаемый результат:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/qicm.kz/fullchain.pem
```

### Шаг 5.4 — вернуть production nginx.conf

```bash
cp docker/nginx/nginx.conf.prod docker/nginx/nginx.conf
docker compose down nginx
```

---

## 6. Первый запуск всего стека

```bash
docker compose up -d --build
```

Порядок старта автоматический: `db` → `web` → `scheduler`, `nginx`, `certbot`.

Проверить что всё поднялось:

```bash
docker compose ps
```

Ожидаемый вывод:
```
NAME                STATUS
invest_db           Up (healthy)
invest_web          Up
invest_scheduler    Up
invest_nginx        Up
invest_certbot      Up
```

---

## 7. Создать суперпользователя Django

```bash
docker compose exec web python manage.py createsuperuser
```

---

## 8. Загрузить начальные данные

Все данные одной командой:

```bash
docker compose exec web sh /app/docker/init_data.sh
```

Или по одному:

```bash
# Главный офис (адрес, телефон, email — используется в навигации)
docker compose exec web python manage.py loaddata apps/contacts/fixtures/initial_office.json

# Фонды (Adal Fund LP, Kokzhiyek Fund LP)
docker compose exec web python manage.py loaddata apps/holdings/fixtures/initial_funds.json

# Команда (руководство + совет директоров с биографиями)
docker compose exec web python manage.py loaddata apps/core/fixtures/initial_team.json
```

### Что загружается

| Fixture | Содержимое |
|---------|------------|
| `initial_office.json` | Главный офис: Астана, пр. Мәңгілік Ел 55А, +7(7172)554-222, info@qicm.kz |
| `initial_funds.json` | 2 фонда (Adal Fund LP, Kokzhiyek Fund LP) + 6 целей |
| `initial_team.json` | 6 членов команды (4 руководство, 2 совет директоров) + биографии |

### Обновить данные через admin

После загрузки все данные редактируются в Django admin (`/admin/`):

- **Офис** → Contacts → Офисы
- **Фонды** → Holdings → Фонды
- **Команда** → Core → Члены команды

---

## 9. Проверка

```bash
# Сайт отдаёт 200
curl -I https://qicm.kz

# HTTP редиректит на HTTPS
curl -I http://qicm.kz
# Ожидается: 301 -> https://qicm.kz

# SSL сертификат валидный
curl -vI https://qicm.kz 2>&1 | grep -E "SSL|expire|issuer"

# Django admin доступен
curl -I https://qicm.kz/admin/

# Статика отдаётся напрямую через nginx (не через Django)
curl -I https://qicm.kz/static/css/styles.css
# Ожидается заголовок: Cache-Control: public, immutable

# Парсер новостей работает
docker compose exec scheduler python /app/src/manage.py fetch_external_news --limit 3
```

---

## 10. Логи

```bash
# Все сервисы
docker compose logs -f

# Только web (Django/gunicorn)
docker compose logs -f web

# Только nginx
docker compose logs -f nginx

# Планировщик новостей
docker compose exec scheduler tail -f /app/var/logs/scheduler.log

# Django логи (внутри контейнера)
docker compose exec web tail -f /app/var/logs/django.log
```

---

## Обновление кода (deploy новой версии)

```bash
cd /home/deploy/app

# Получить изменения
git pull origin main

# Пересобрать и перезапустить без даунтайма
docker compose up -d --build web scheduler

# Проверить
docker compose ps
docker compose logs -f web
```

> `nginx` и `db` не требуют пересборки при обновлении кода.

---

## Резервное копирование БД

```bash
# Создать дамп
docker compose exec db pg_dump -U invest_admin invest_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановить из дампа
docker compose exec -T db psql -U invest_admin invest_db < backup_20260101_120000.sql
```

Настроить автоматический бэкап (cron на сервере):

```bash
crontab -e
# Добавить:
0 3 * * * cd /home/deploy/app && docker compose exec -T db pg_dump -U invest_admin invest_db > /home/deploy/backups/db_$(date +\%Y\%m\%d).sql
```

---

## Частые проблемы

### nginx не стартует — нет сертификата
Пройти шаг 5 (bootstrap).

### `502 Bad Gateway`
```bash
docker compose logs web  # gunicorn упал?
docker compose logs db   # БД не готова?
docker compose restart web
```

### `CSRF verification failed`
Проверить `.env`:
```
CSRF_TRUSTED_ORIGINS=https://qicm.kz,https://www.qicm.kz
```

### Статика не отдаётся (404 на /static/)
```bash
docker compose exec web python manage.py collectstatic --noinput
docker compose restart nginx
```

### Сертификат не обновился автоматически
```bash
docker compose exec certbot certbot renew --dry-run
```

### Посмотреть когда истекает сертификат
```bash
docker compose exec certbot certbot certificates
```
