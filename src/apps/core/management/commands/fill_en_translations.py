"""
Заполняет пустые _en поля для Fund, FundGoal, Office данными из аудита (Сайт.pdf).

Безопасно: трогает только записи с пустым _en полем, ничего не перезатирает.
Если структура на проде отличается (другие фонды/офисы) — печатает что не нашёл,
ничего не падает.

Usage:
    python manage.py fill_en_translations           # применить
    python manage.py fill_en_translations --dry-run # только показать что будет сделано
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.holdings.models import Fund, FundGoal
from apps.contacts.models import Office


FUND_DATA = {
    'Adal Fund LP': {
        'name_en': 'Adal Fund LP',
        'badge_en': 'Open-ended fund',
        'fund_type_en': 'Fund Structure: open-ended specialised umbrella private equity fund',
        'target_size_en': '$1 billion',
        'lifespan_en': '10 years',
    },
    'Kokzhiyek Fund LP': {
        'name_en': 'Kokzhiyek Fund LP',
        'badge_en': 'Closed-end fund',
        'fund_type_en': 'Fund Structure: closed-end private equity fund',
        'target_size_en': '$4 billion',
        'lifespan_en': '40 years',
    },
}

GOAL_TRANSLATIONS = {
    'Расширение экспортного потенциала аграрного сектора Республики Казахстан.':
        'Expanding the export potential of the agricultural sector of the Republic of Kazakhstan.',
    'Обеспечение стабильных каналов сбыта для отечественных производителей.':
        'Ensuring stable sales channels for domestic producers.',
    'Привлечение долгосрочного иностранного капитала в цепочки добавленной стоимости агропромышленного комплекса (АПК).':
        'Attracting long-term foreign capital into the value chains of the agro-industrial complex (AIC).',
    'Поддержка крупнейших предприятий Республики Казахстан.':
        'Supporting the largest enterprises of the Republic of Kazakhstan.',
    'Увеличение объемов производства продукции и повышение экспортного потенциала.':
        'Increasing production volumes and enhancing export potential.',
    'Проведение модернизации и увеличение существующих производственных мощностей.':
        'Modernising and expanding existing production capacities.',
}

OFFICE_DATA = {
    'city_en': 'Astana',
    'address_en': 'Yesil district, 55A Mangilik El Ave., Block C, Z05T2H3, Astana, Republic of Kazakhstan',
    'working_hours_en': 'Monday-Friday: 08:30-18:00 (Astana, GMT+5)',
}


class Command(BaseCommand):
    help = 'Заполняет пустые EN переводы для Fund/FundGoal/Office (только пустые поля, не перезатирает)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Только показать изменения, не сохранять')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        changed = 0

        self.stdout.write('=== Funds ===')
        for fund in Fund.objects.all():
            data = FUND_DATA.get(fund.name)
            if not data:
                self.stdout.write(self.style.WARNING(f'  Пропущен (нет данных): {fund.name}'))
                continue

            updates = {}
            for field in ('name_en', 'badge_en', 'fund_type_en', 'target_size_en', 'lifespan_en'):
                if not getattr(fund, field) and data.get(field):
                    updates[field] = data[field]

            if not updates:
                self.stdout.write(f'  {fund.name}: уже заполнено, пропуск')
                continue

            self.stdout.write(f'  {fund.name}: {updates}')
            changed += 1
            if not dry_run:
                for field, value in updates.items():
                    setattr(fund, field, value)
                fund.save()

        self.stdout.write('=== Fund Goals ===')
        for goal in FundGoal.objects.all():
            if goal.text_en:
                continue
            translation = GOAL_TRANSLATIONS.get(goal.text.strip())
            if not translation:
                self.stdout.write(self.style.WARNING(f'  Пропущен (нет перевода): {goal.text[:50]}'))
                continue
            self.stdout.write(f'  goal#{goal.pk}: -> {translation[:50]}...')
            changed += 1
            if not dry_run:
                goal.text_en = translation
                goal.save()

        self.stdout.write('=== Offices ===')
        for office in Office.objects.filter(is_main=True):
            updates = {}
            for field, value in OFFICE_DATA.items():
                if not getattr(office, field):
                    updates[field] = value

            if not updates:
                self.stdout.write(f'  {office.city}: уже заполнено, пропуск')
                continue

            self.stdout.write(f'  {office.city} (pk={office.pk}): {updates}')
            changed += 1
            if not dry_run:
                for field, value in updates.items():
                    setattr(office, field, value)
                office.save()

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nDRY RUN: {changed} записей будет изменено. Запустите без --dry-run для применения.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nГотово: {changed} записей обновлено.'))
