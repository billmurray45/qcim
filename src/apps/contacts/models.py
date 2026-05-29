from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """
    Модель для хранения сообщений из формы обратной связи.
    """

    class MessageSubject(models.TextChoices):
        INVESTMENT = 'investment', _('Инвестиционные проекты')
        CONSULTING = 'consulting', _('Консультации')
        PARTNERSHIP = 'partnership', _('Сотрудничество')
        OTHER = 'other', _('Другое')

    class MessageStatus(models.TextChoices):
        NEW = 'new', _('Новая')
        READ = 'read', _('Прочитано')
        IN_PROGRESS = 'in_progress', _('В обработке')
        REPLIED = 'replied', _('Ответ отправлен')
        CANCELLED = 'cancelled', _('Отменена')

    # Пользователь (если авторизован)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages',
        verbose_name=_('пользователь')
    )

    # Основные поля
    name = models.CharField(_('имя'), max_length=150)
    email = models.EmailField(_('email'))
    phone = models.CharField(_('телефон'), max_length=20)
    subject = models.CharField(
        _('тема'),
        max_length=20,
        choices=MessageSubject.choices,
        default=MessageSubject.OTHER,
    )
    message = models.TextField(_('сообщение'))

    # Метаданные
    ip_address = models.GenericIPAddressField(_('IP адрес'), null=True, blank=True)
    user_agent = models.CharField(_('User Agent'), max_length=500, blank=True)

    # Статус
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=MessageStatus.choices,
        default=MessageStatus.NEW,
    )
    is_read = models.BooleanField(_('прочитано'), default=False)
    is_replied = models.BooleanField(_('ответ отправлен'), default=False)

    # Даты
    created_at = models.DateTimeField(_('дата создания'), default=timezone.now)
    read_at = models.DateTimeField(_('дата прочтения'), null=True, blank=True)

    class Meta:
        verbose_name = _('сообщение')
        verbose_name_plural = _('сообщения')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['email']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.name} - {self.get_subject_display()} ({self.created_at.strftime("%d.%m.%Y %H:%M")})'

    def mark_as_read(self):
        """Отметить сообщение как прочитанное."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            if self.status == self.MessageStatus.NEW:
                self.status = self.MessageStatus.READ
                self.save(update_fields=['is_read', 'read_at', 'status'])
            else:
                self.save(update_fields=['is_read', 'read_at'])

    def mark_as_replied(self):
        """Отметить что на сообщение ответили."""
        if not self.is_replied:
            self.is_replied = True
            self.status = self.MessageStatus.REPLIED
            self.save(update_fields=['is_replied', 'status'])

    def can_cancel(self):
        """Проверить, можно ли отменить заявку."""
        return self.status in [self.MessageStatus.NEW, self.MessageStatus.READ]

    def cancel(self):
        """Отменить заявку."""
        if self.can_cancel():
            self.status = self.MessageStatus.CANCELLED
            self.save(update_fields=['status'])
            return True
        return False

    def get_status_badge_class(self):
        """Возвращает CSS класс для бейджа статуса."""
        status_classes = {
            self.MessageStatus.NEW: 'status--new',
            self.MessageStatus.READ: 'status--read',
            self.MessageStatus.IN_PROGRESS: 'status--progress',
            self.MessageStatus.REPLIED: 'status--replied',
            self.MessageStatus.CANCELLED: 'status--cancelled',
        }
        return status_classes.get(self.status, 'status--new')


class Office(models.Model):
    """Офисы компании"""

    city = models.CharField(_('город'), max_length=100)
    city_kk = models.CharField(_('город (казахский)'), max_length=100, blank=True)
    city_en = models.CharField(_('город (английский)'), max_length=100, blank=True)
    address = models.CharField(_('адрес'), max_length=255)
    address_kk = models.CharField(_('адрес (казахский)'), max_length=255, blank=True)
    address_en = models.CharField(_('адрес (английский)'), max_length=255, blank=True)
    phone = models.CharField(_('телефон'), max_length=50)
    email = models.EmailField(_('email'), blank=True)
    working_hours = models.CharField(_('режим работы'), max_length=200, default='Пн-Пт 9:00-18:00')
    working_hours_kk = models.CharField(_('режим работы (казахский)'), max_length=200, blank=True)
    working_hours_en = models.CharField(_('режим работы (английский)'), max_length=200, blank=True)

    # Координаты для карты
    latitude = models.DecimalField(
        _('широта'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Например: 51.169392'
    )
    longitude = models.DecimalField(
        _('долгота'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='Например: 71.449074'
    )

    # Социальные сети
    instagram = models.URLField(_('Instagram'), blank=True, help_text='Ссылка на профиль Instagram')
    facebook = models.URLField(_('Facebook'), blank=True, help_text='Ссылка на страницу Facebook')
    linkedin = models.URLField(_('LinkedIn'), blank=True, help_text='Ссылка на профиль LinkedIn')
    twitter = models.URLField(_('Twitter/X'), blank=True, help_text='Ссылка на профиль Twitter/X')
    youtube = models.URLField(_('YouTube'), blank=True, help_text='Ссылка на канал YouTube')
    telegram = models.CharField(_('Telegram'), max_length=100, blank=True, help_text='Username или ссылка на канал')
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True, help_text='Номер телефона для WhatsApp')
    tiktok = models.URLField(_('TikTok'), blank=True, help_text='Ссылка на профиль TikTok')

    is_main = models.BooleanField(_('главный офис'), default=False)
    is_active = models.BooleanField(_('активен'), default=True)
    order = models.PositiveIntegerField(_('порядок'), default=0)

    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('офис')
        verbose_name_plural = _('офисы')
        ordering = ['order', 'city']

    def __str__(self):
        return f'{self.city} - {self.address}'

    def save(self, *args, **kwargs):
        # Если это главный офис, сбросить флаг у остальных
        if self.is_main:
            Office.objects.filter(is_main=True).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)

    def get_social_media(self):
        """Возвращает словарь с активными социальными сетями."""
        social_media = {}

        if self.instagram:
            social_media['instagram'] = {
                'name': 'Instagram',
                'url': self.instagram,
                'icon': 'fab fa-instagram'
            }
        if self.facebook:
            social_media['facebook'] = {
                'name': 'Facebook',
                'url': self.facebook,
                'icon': 'fab fa-facebook-f'
            }
        if self.linkedin:
            social_media['linkedin'] = {
                'name': 'LinkedIn',
                'url': self.linkedin,
                'icon': 'fab fa-linkedin-in'
            }
        if self.twitter:
            social_media['twitter'] = {
                'name': 'Twitter/X',
                'url': self.twitter,
                'icon': 'fab fa-twitter'
            }
        if self.youtube:
            social_media['youtube'] = {
                'name': 'YouTube',
                'url': self.youtube,
                'icon': 'fab fa-youtube'
            }
        if self.telegram:
            # Если это username, добавляем https://t.me/
            url = self.telegram
            if not url.startswith('http'):
                url = f'https://t.me/{url.lstrip("@")}'
            social_media['telegram'] = {
                'name': 'Telegram',
                'url': url,
                'icon': 'fab fa-telegram-plane'
            }
        if self.whatsapp:
            # Форматируем номер для WhatsApp ссылки
            phone = self.whatsapp.replace('+', '').replace(' ', '').replace('-', '')
            social_media['whatsapp'] = {
                'name': 'WhatsApp',
                'url': f'https://wa.me/{phone}',
                'icon': 'fab fa-whatsapp'
            }
        if self.tiktok:
            social_media['tiktok'] = {
                'name': 'TikTok',
                'url': self.tiktok,
                'icon': 'fab fa-tiktok'
            }

        return social_media

    def has_social_media(self):
        """Проверяет, есть ли хотя бы одна соцсеть."""
        return bool(self.get_social_media())
