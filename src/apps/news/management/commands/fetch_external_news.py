import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from apps.news.models import ExternalNews

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

BAITEREK_URL = 'https://baiterek.gov.kz/ru/pr/news/list//?filter=holdingFilter'
BAITEREK_BASE = 'https://baiterek.gov.kz'

QIC_URL = 'https://qic.kz/ru/novosti-i-insayty/'
QIC_BASE = 'https://qic.kz'


def parse_date_dot(date_str):
    """Парсит дату вида 03.04.2026"""
    try:
        return datetime.strptime(date_str.strip(), '%d.%m.%Y').date()
    except (ValueError, AttributeError):
        return datetime.today().date()


def fetch_baiterek(limit=6):
    """Получает последние N новостей с baiterek.gov.kz"""
    try:
        resp = requests.get(BAITEREK_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе Байтерек: {e}')
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    items = soup.select('a.news-item')[:limit]

    results = []
    for item in items:
        raw_id = item.get('id', '')
        external_id = raw_id.split('_')[-1] if raw_id else ''

        title_tag = item.find('h2')
        title = title_tag.get_text(strip=True) if title_tag else item.get('title', '')

        href = item.get('href', '')
        url = BAITEREK_BASE + href if href.startswith('/') else href

        img_tag = item.select_one('.preview_picture')
        image_url = ''
        if img_tag:
            style = img_tag.get('style', '')
            if "url('" in style:
                image_url = style.split("url('")[1].split("')")[0]
                if image_url.startswith('/'):
                    image_url = BAITEREK_BASE + image_url

        date_tag = item.select_one('.news-date-time')
        published_date = parse_date_dot(date_tag.get_text() if date_tag else '')

        if external_id and title and url:
            results.append({
                'source': ExternalNews.SOURCE_BAITEREK,
                'external_id': external_id,
                'title': title,
                'url': url,
                'image_url': image_url,
                'published_date': published_date,
            })

    return results


def fetch_qic(limit=6):
    """Получает последние N новостей с qic.kz"""
    try:
        resp = requests.get(QIC_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе QIC: {e}')
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Карточки новостей: div.carousel_block_1
    items = soup.select('div.carousel_block_1')[:limit]

    results = []
    for item in items:
        raw_id = item.get('id', '')
        external_id = raw_id.split('_')[-1] if raw_id else ''

        # Заголовок — ссылка .carousel_block_2_link
        link_tag = item.select_one('a.carousel_block_2_link')
        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        href = link_tag.get('href', '')
        url = QIC_BASE + href if href.startswith('/') else href

        # Изображение
        img_tag = item.select_one('picture img')
        image_url = ''
        if img_tag:
            src = img_tag.get('src', '')
            if src.startswith('/'):
                image_url = QIC_BASE + src
            else:
                image_url = src

        # Дата
        date_tag = item.select_one('.carousel_block_1_location')
        published_date = datetime.today().date()
        if date_tag:
            text = date_tag.get_text(strip=True).split()[0]
            published_date = parse_date_dot(text)

        if not external_id:
            # Используем часть URL как fallback ID
            external_id = href.strip('/').split('/')[-1][:80]

        if title and url:
            results.append({
                'source': ExternalNews.SOURCE_QIC,
                'external_id': external_id,
                'title': title,
                'url': url,
                'image_url': image_url,
                'published_date': published_date,
            })

    return results


class Command(BaseCommand):
    help = 'Парсинг внешних новостей (Байтерек, QIC)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=6,
            help='Количество новостей для загрузки (по умолчанию 6)',
        )
        parser.add_argument(
            '--source',
            type=str,
            default='all',
            choices=['all', 'baiterek', 'qic'],
            help='Источник для парсинга',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        source = options['source']
        created_total = 0
        updated_total = 0

        def save_items(items):
            nonlocal created_total, updated_total
            for data in items:
                obj, created = ExternalNews.objects.update_or_create(
                    source=data['source'],
                    external_id=data['external_id'],
                    defaults={
                        'title': data['title'],
                        'url': data['url'],
                        'image_url': data['image_url'],
                        'published_date': data['published_date'],
                    }
                )
                if created:
                    created_total += 1
                else:
                    updated_total += 1

        if source in ('all', 'baiterek'):
            self.stdout.write('Парсинг Байтерек...')
            items = fetch_baiterek(limit=limit)
            if not items:
                logger.warning('Байтерек: парсер вернул 0 новостей — возможно изменилась структура сайта')
            save_items(items)
            self.stdout.write(f'  Байтерек: {len(items)} новостей обработано')

        if source in ('all', 'qic'):
            self.stdout.write('Парсинг QIC...')
            items = fetch_qic(limit=limit)
            if not items:
                logger.warning('QIC: парсер вернул 0 новостей — возможно изменилась структура сайта')
            save_items(items)
            self.stdout.write(f'  QIC: {len(items)} новостей обработано')

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово. Создано: {created_total}, обновлено: {updated_total}'
            )
        )
