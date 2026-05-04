from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Администратор')
        EDITOR = 'EDITOR', _('Редактор')
        CONTENT_MANAGER = 'CONTENT_MANAGER', _('Контент-менеджер')
        VIEWER = 'VIEWER', _('Наблюдатель')

    email = models.EmailField(_('email адрес'), unique=True)
    first_name = models.CharField(_('имя'), max_length=150, blank=True)
    last_name = models.CharField(_('фамилия'), max_length=150, blank=True)

    # Дополнительные поля
    phone = models.CharField(_('телефон'), max_length=20, blank=True)
    position = models.CharField(_('должность'), max_length=100, blank=True)
    role = models.CharField(
        _('роль'),
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
    )

    # Статусы
    is_staff = models.BooleanField(_('статус персонала'), default=False)
    is_active = models.BooleanField(_('активен'), default=True)

    # Даты
    date_joined = models.DateTimeField(_('дата регистрации'), default=timezone.now)
    last_login = models.DateTimeField(_('последний вход'), blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.first_name or self.email
