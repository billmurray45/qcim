from django.db import models
from django.utils.translation import gettext_lazy as _


class Fund(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    badge = models.CharField(_('Бейдж'), max_length=100, default='', help_text='Например: Открытый фонд')
    fund_type = models.CharField(_('Тип фонда'), max_length=255)
    target_size = models.CharField(_('Целевой размер'), max_length=100, help_text='Например: $1 млрд')
    lifespan = models.CharField(_('Срок жизни'), max_length=50, default='', help_text='Например: 10 лет')
    registration_date = models.DateField(_('Дата регистрации'))
    is_dark = models.BooleanField(_('Тёмная карточка'), default=False)
    is_active = models.BooleanField(_('Активен'), default=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Фонд')
        verbose_name_plural = _('Фонды')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class FundGoal(models.Model):
    fund = models.ForeignKey(Fund, related_name='goals', on_delete=models.CASCADE)
    text = models.CharField(_('Цель'), max_length=500)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Цель фонда')
        verbose_name_plural = _('Цели фонда')
        ordering = ['order']

    def __str__(self):
        return self.text[:60]
