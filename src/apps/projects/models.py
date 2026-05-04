from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from apps.news.models import transliterate_to_slug


class ProjectCategory(models.Model):
    """Категория инвестиционного проекта"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_('URL слаг')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Иконка (FontAwesome класс)')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Категория проекта')
        verbose_name_plural = _('Категории проектов')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_to_slug(self.name)
        super().save(*args, **kwargs)


class ProjectStatus(models.TextChoices):
    """Статусы проекта"""
    PLANNING = 'planning', _('Планирование')
    ACTIVE = 'active', _('Активный')
    COMPLETED = 'completed', _('Завершен')
    SUSPENDED = 'suspended', _('Приостановлен')


class Project(models.Model):
    """Инвестиционный проект"""

    # Основное
    title = models.CharField(
        max_length=255,
        verbose_name=_('Название проекта')
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_('URL слаг')
    )

    # Связи
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_('Категория')
    )

    # Контент
    short_description = models.TextField(
        max_length=500,
        verbose_name=_('Краткое описание')
    )
    description = models.TextField(
        verbose_name=_('Полное описание')
    )

    image = models.ImageField(
        upload_to='projects/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Главное изображение')
    )
    gallery = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_('Галерея изображений (URLs)')
    )

    # Финансовые данные
    investment_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Сумма инвестиций')
    )
    currency = models.CharField(
        max_length=3,
        default='KZT',
        verbose_name=_('Валюта')
    )
    expected_roi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Ожидаемая доходность (%)')
    )

    # Даты
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата начала')
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата окончания')
    )

    # Статус
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.PLANNING,
        verbose_name=_('Статус проекта')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Избранный проект')
    )

    # Локация
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Местоположение (город/регион)')
    )
    country = models.CharField(
        max_length=100,
        default='Kazakhstan',
        verbose_name=_('Страна')
    )

    # Партнеры
    partners = models.TextField(
        blank=True,
        verbose_name=_('Партнеры/инвесторы')
    )

    # SEO поля
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('SEO заголовок')
    )
    meta_description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('SEO описание')
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('SEO ключевые слова')
    )

    # Статистика
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество просмотров')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Опубликовано')
    )
    published_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Дата публикации')
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_to_slug(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.short_description
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Увеличить счетчик просмотров"""
        Project.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])

    @property
    def status_badge_class(self):
        """CSS класс для badge статуса"""
        return {
            'planning': 'badge--blue',
            'active': 'badge--green',
            'completed': 'badge--gray',
            'suspended': 'badge--red',
        }.get(self.status, 'badge--default')
