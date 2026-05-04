from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone


def transliterate_to_slug(text):
    """Транслитерация кириллицы в латиницу для slug"""
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }

    result = []
    for char in text:
        result.append(translit_dict.get(char, char))

    transliterated = ''.join(result)
    return slugify(transliterated)


class Category(models.Model):
    """Категория новостей"""

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
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_to_slug(self.name)
        super().save(*args, **kwargs)


class News(models.Model):
    """Новость"""

    title = models.CharField(
        max_length=255,
        verbose_name=_('Заголовок')
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name=_('URL слаг')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news',
        verbose_name=_('Категория')
    )
    excerpt = models.TextField(
        max_length=500,
        verbose_name=_('Краткое описание')
    )
    content = models.TextField(
        verbose_name=_('Содержание')
    )
    image = models.ImageField(
        upload_to='news/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Изображение')
    )

    # Даты
    published_date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Дата публикации')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Опубликовано')
    )

    # Статистика
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество просмотров')
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
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = transliterate_to_slug(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.excerpt
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Увеличить счетчик просмотров"""
        News.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])


class ExternalNews(models.Model):
    """Новости из внешних источников (парсинг)"""

    SOURCE_BAITEREK = 'baiterek'
    SOURCE_QIC = 'qic'

    SOURCE_CHOICES = [
        (SOURCE_BAITEREK, 'Байтерек'),
        (SOURCE_QIC, 'QIC'),
    ]

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        verbose_name=_('Источник')
    )
    external_id = models.CharField(
        max_length=100,
        verbose_name=_('Внешний ID')
    )
    title = models.CharField(
        max_length=500,
        verbose_name=_('Заголовок')
    )
    url = models.URLField(
        max_length=1000,
        verbose_name=_('Ссылка')
    )
    image_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name=_('URL изображения')
    )
    published_date = models.DateField(
        verbose_name=_('Дата публикации')
    )
    fetched_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Внешняя новость')
        verbose_name_plural = _('Внешние новости')
        ordering = ['-published_date']
        unique_together = [('source', 'external_id')]

    def __str__(self):
        return f'[{self.get_source_display()}] {self.title}'
