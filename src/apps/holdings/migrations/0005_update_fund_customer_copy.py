# Generated manually from customer copy review.

from django.db import migrations


def update_fund_copy(apps, schema_editor):
    Fund = apps.get_model('holdings', 'Fund')

    updates = {
        'Adal Fund LP': 'Fund Structure: open-ended specialised umbrella private equity fund',
        'Kokzhiyek Fund LP': 'Fund Structure: closed-end private equity fund',
    }

    for name, fund_type_en in updates.items():
        Fund.objects.filter(name=name).update(fund_type_en=fund_type_en)


class Migration(migrations.Migration):

    dependencies = [
        ('holdings', '0004_fund_badge_en_fund_badge_kk_fund_fund_type_en_and_more'),
    ]

    operations = [
        migrations.RunPython(update_fund_copy, migrations.RunPython.noop),
    ]
