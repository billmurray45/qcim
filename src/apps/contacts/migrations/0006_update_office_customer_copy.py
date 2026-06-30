# Generated manually from customer copy review.

from django.db import migrations, models


def update_office_copy(apps, schema_editor):
    Office = apps.get_model('contacts', 'Office')

    values = {
        'working_hours': 'Пн-Пт: 08:30-18:00 (Астана, GMT+5)',
        'working_hours_kk': 'Дс-Жм: 08:30-18:00 (Астана, GMT+5)',
        'working_hours_en': 'Monday-Friday: 08:30-18:00 (Astana, GMT+5)',
        'address_en': (
            'Yesil district, 55A Mangilik El Ave., Block C, Z05T2H3, '
            'Astana, Republic of Kazakhstan'
        ),
    }

    qs = Office.objects.filter(is_main=True)
    if not qs.exists():
        qs = Office.objects.filter(pk=1)
    qs.update(**values)


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_office_address_en_office_address_kk_office_city_en_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='office',
            name='working_hours',
            field=models.CharField(
                default='Пн-Пт: 08:30-18:00 (Астана, GMT+5)',
                max_length=200,
                verbose_name='режим работы',
            ),
        ),
        migrations.RunPython(update_office_copy, migrations.RunPython.noop),
    ]
