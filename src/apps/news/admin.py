from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Category, News, ExternalNews


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active_status_icon', 'news_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def active_status_icon(self, obj):
        """Отображение активности категории с иконкой"""
        if obj.is_active:
            return mark_safe('<i class="fas fa-check-circle" style="color: #28a745; font-size: 16px;"></i>')
        return mark_safe('<i class="fas fa-times-circle" style="color: #dc3545; font-size: 16px;"></i>')
    active_status_icon.short_description = 'Активна'

    def news_count(self, obj):
        """Количество новостей в категории"""
        count = obj.news.filter(is_published=True).count()
        return count
    news_count.short_description = 'Новостей'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'published_date',
        'published_status_icon',
        'views_count',
        'image_preview',
        'created_at'
    ]
    list_filter = ['is_published', 'category', 'published_date', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'

    def get_readonly_fields(self, request, obj=None):
        """Показывать превью только при редактировании существующего объекта"""
        if obj:  # Редактирование существующего объекта
            return ['views_count', 'created_at', 'updated_at', 'image_preview']
        else:  # Создание нового объекта
            return ['views_count', 'created_at', 'updated_at']

    def get_fieldsets(self, request, obj=None):
        """Разные fieldsets для создания и редактирования"""
        if obj:  # Редактирование - показываем превью
            return (
                ('Основная информация', {
                    'fields': ('title', 'slug', 'category', 'excerpt')
                }),
                ('Содержание', {
                    'fields': ('content', 'image', 'image_preview')
                }),
                ('Публикация', {
                    'fields': ('published_date', 'is_published')
                }),
                ('SEO', {
                    'fields': ('meta_title', 'meta_description', 'meta_keywords'),
                    'classes': ('collapse',)
                }),
                ('Статистика', {
                    'fields': ('views_count', 'created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        else:  # Создание - без превью
            return (
                ('Основная информация', {
                    'fields': ('title', 'slug', 'category', 'excerpt')
                }),
                ('Содержание', {
                    'fields': ('content', 'image')
                }),
                ('Публикация', {
                    'fields': ('published_date', 'is_published')
                }),
                ('SEO', {
                    'fields': ('meta_title', 'meta_description', 'meta_keywords'),
                    'classes': ('collapse',)
                }),
            )

    def published_status_icon(self, obj):
        """Отображение статуса публикации с иконкой"""
        if obj.is_published:
            return mark_safe('<i class="fas fa-check-circle" style="color: #28a745; font-size: 16px;"></i>')
        return mark_safe('<i class="fas fa-times-circle" style="color: #dc3545; font-size: 16px;"></i>')
    published_status_icon.short_description = 'Опубликовано'

    def image_preview(self, obj):
        """Превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Превью'

    actions = ['publish_news', 'unpublish_news']

    def publish_news(self, request, queryset):
        """Опубликовать выбранные новости"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Опубликовано новостей: {updated}')
    publish_news.short_description = 'Опубликовать выбранные новости'

    def unpublish_news(self, request, queryset):
        """Снять с публикации выбранные новости"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Снято с публикации новостей: {updated}')
    unpublish_news.short_description = 'Снять с публикации выбранные новости'


@admin.register(ExternalNews)
class ExternalNewsAdmin(admin.ModelAdmin):
    list_display = ["title", "source", "published_date", "fetched_at", "url"]
    list_filter = ["source", "published_date"]
    search_fields = ["title"]
    readonly_fields = ["source", "external_id", "title", "url", "image_url", "published_date", "fetched_at"]
    ordering = ["-published_date"]
