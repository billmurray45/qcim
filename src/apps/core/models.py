from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language


def localized_model_field(instance, field_name):
    language = (get_language() or 'ru').split('-')[0]
    if language in {'kk', 'en'}:
        value = getattr(instance, f'{field_name}_{language}', None)
        if value:
            return value
    return getattr(instance, field_name, '') or ''


class TeamMember(models.Model):
    class Group(models.TextChoices):
        MANAGEMENT = 'management', _('Руководство')
        BOARD = 'board', _('Совет директоров')

    first_name = models.CharField(_('Имя'), max_length=100)
    first_name_kk = models.CharField(_('Имя (казахский)'), max_length=100, blank=True)
    first_name_en = models.CharField(_('Имя (английский)'), max_length=100, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=100)
    last_name_kk = models.CharField(_('Фамилия (казахский)'), max_length=100, blank=True)
    last_name_en = models.CharField(_('Фамилия (английский)'), max_length=100, blank=True)
    middle_name = models.CharField(_('Отчество'), max_length=100, blank=True)
    middle_name_kk = models.CharField(_('Отчество (казахский)'), max_length=100, blank=True)
    middle_name_en = models.CharField(_('Отчество (английский)'), max_length=100, blank=True)
    position = models.CharField(_('Должность'), max_length=255)
    position_kk = models.CharField(_('Должность (казахский)'), max_length=255, blank=True)
    position_en = models.CharField(_('Должность (английский)'), max_length=255, blank=True)
    group = models.CharField(_('Группа'), max_length=20, choices=Group.choices, default=Group.MANAGEMENT)
    photo = models.ImageField(_('Фото'), upload_to='team/', blank=True, null=True)
    citizenship = models.CharField(_('Гражданство'), max_length=100, default='Республика Казахстан')
    citizenship_kk = models.CharField(_('Гражданство (казахский)'), max_length=100, blank=True)
    citizenship_en = models.CharField(_('Гражданство (английский)'), max_length=100, blank=True)
    is_active = models.BooleanField(_('Активен'), default=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Член команды')
        verbose_name_plural = _('Команда')
        ordering = ['group', 'order', 'last_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def get_initials(self):
        parts = [localized_model_field(self, 'last_name'), localized_model_field(self, 'first_name')]
        return ''.join(p[0] for p in parts if p)

    def get_full_name(self):
        parts = [
            localized_model_field(self, 'last_name'),
            localized_model_field(self, 'first_name'),
            localized_model_field(self, 'middle_name'),
        ]
        return ' '.join(p for p in parts if p)


class TeamMemberBioSection(models.Model):
    member = models.ForeignKey(TeamMember, related_name='bio_sections', on_delete=models.CASCADE)
    title = models.CharField(_('Заголовок'), max_length=200, help_text='Например: Сведения о трудовой деятельности')
    title_kk = models.CharField(_('Заголовок (казахский)'), max_length=200, blank=True)
    title_en = models.CharField(_('Заголовок (английский)'), max_length=200, blank=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Раздел биографии')
        verbose_name_plural = _('Разделы биографии')
        ordering = ['order']

    def __str__(self):
        return f'{self.member} — {self.title}'


class TeamMemberBioItem(models.Model):
    section = models.ForeignKey(TeamMemberBioSection, related_name='items', on_delete=models.CASCADE)
    text = models.TextField(_('Текст'))
    text_kk = models.TextField(_('Текст (казахский)'), blank=True)
    text_en = models.TextField(_('Текст (английский)'), blank=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Пункт биографии')
        verbose_name_plural = _('Пункты биографии')
        ordering = ['order']

    def __str__(self):
        return self.text[:60]
