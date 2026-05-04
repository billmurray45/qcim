from django.db import models
from django.utils.translation import gettext_lazy as _


class TeamMember(models.Model):
    class Group(models.TextChoices):
        MANAGEMENT = 'management', _('Руководство')
        BOARD = 'board', _('Совет директоров')

    first_name = models.CharField(_('Имя'), max_length=100)
    last_name = models.CharField(_('Фамилия'), max_length=100)
    middle_name = models.CharField(_('Отчество'), max_length=100, blank=True)
    position = models.CharField(_('Должность'), max_length=255)
    group = models.CharField(_('Группа'), max_length=20, choices=Group.choices, default=Group.MANAGEMENT)
    photo = models.ImageField(_('Фото'), upload_to='team/', blank=True, null=True)
    citizenship = models.CharField(_('Гражданство'), max_length=100, default='Республика Казахстан')
    is_active = models.BooleanField(_('Активен'), default=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Член команды')
        verbose_name_plural = _('Команда')
        ordering = ['group', 'order', 'last_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def get_initials(self):
        parts = [self.last_name, self.first_name]
        return ''.join(p[0] for p in parts if p)

    def get_full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p)


class TeamMemberBioSection(models.Model):
    member = models.ForeignKey(TeamMember, related_name='bio_sections', on_delete=models.CASCADE)
    title = models.CharField(_('Заголовок'), max_length=200, help_text='Например: Сведения о трудовой деятельности')
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
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Пункт биографии')
        verbose_name_plural = _('Пункты биографии')
        ordering = ['order']

    def __str__(self):
        return self.text[:60]
