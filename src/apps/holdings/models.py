from django.db import models
from django.utils.translation import gettext_lazy as _


class Fund(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    name_kk = models.CharField(_('Название (казахский)'), max_length=255, blank=True)
    name_en = models.CharField(_('Название (английский)'), max_length=255, blank=True)
    badge = models.CharField(_('Бейдж'), max_length=100, default='', help_text='Например: Открытый фонд')
    badge_kk = models.CharField(_('Бейдж (казахский)'), max_length=100, blank=True)
    badge_en = models.CharField(_('Бейдж (английский)'), max_length=100, blank=True)
    fund_type = models.CharField(_('Тип фонда'), max_length=255)
    fund_type_kk = models.CharField(_('Тип фонда (казахский)'), max_length=255, blank=True)
    fund_type_en = models.CharField(_('Тип фонда (английский)'), max_length=255, blank=True)
    target_size = models.CharField(_('Целевой размер'), max_length=100, help_text='Например: $1 млрд')
    target_size_kk = models.CharField(_('Целевой размер (казахский)'), max_length=100, blank=True)
    target_size_en = models.CharField(_('Целевой размер (английский)'), max_length=100, blank=True)
    lifespan = models.CharField(_('Срок жизни'), max_length=50, default='', help_text='Например: 10 лет')
    lifespan_kk = models.CharField(_('Срок жизни (казахский)'), max_length=50, blank=True)
    lifespan_en = models.CharField(_('Срок жизни (английский)'), max_length=50, blank=True)
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
    text_kk = models.CharField(_('Цель (казахский)'), max_length=500, blank=True)
    text_en = models.CharField(_('Цель (английский)'), max_length=500, blank=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Цель фонда')
        verbose_name_plural = _('Цели фонда')
        ordering = ['order']

    def __str__(self):
        return self.text[:60]
