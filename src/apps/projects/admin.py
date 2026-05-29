from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import ProjectCategory, Project


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active_status_icon', 'project_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'name_kk', 'description_kk', 'name_en', 'description_en']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Русский', {
            'fields': ('name', 'slug', 'description', 'icon', 'is_active')
        }),
        ('Қазақша', {
            'fields': ('name_kk', 'description_kk')
        }),
        ('English', {
            'fields': ('name_en', 'description_en')
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

    def project_count(self, obj):
        """Количество проектов в категории"""
        count = obj.projects.filter(is_published=True).count()
        return count
    project_count.short_description = 'Проектов'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'status_badge',
        'investment_display',
        'published_status_icon',
        'featured_icon',
        'views_count',
        'image_preview',
        'created_at'
    ]
    list_filter = ['status', 'is_published', 'is_featured', 'category', 'published_date', 'created_at']
    search_fields = [
        'title', 'description', 'short_description', 'location',
        'title_kk', 'description_kk', 'short_description_kk', 'location_kk',
        'title_en', 'description_en', 'short_description_en', 'location_en',
    ]
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
                ('Русский', {
                    'fields': ('title', 'slug', 'category', 'short_description')
                }),
                ('Қазақша', {
                    'fields': ('title_kk', 'short_description_kk', 'description_kk')
                }),
                ('English', {
                    'fields': ('title_en', 'short_description_en', 'description_en')
                }),
                ('Полное описание', {
                    'fields': ('description',)
                }),
                ('Медиа', {
                    'fields': ('image', 'image_preview', 'gallery')
                }),
                ('Финансы', {
                    'fields': ('investment_amount', 'currency', 'expected_roi', 'partners', 'partners_kk', 'partners_en')
                }),
                ('Сроки и локация', {
                    'fields': (
                        'start_date', 'end_date',
                        'location', 'location_kk', 'location_en',
                        'country', 'country_kk', 'country_en',
                    )
                }),
                ('Статус', {
                    'fields': ('status', 'is_published', 'is_featured', 'published_date')
                }),
                ('SEO', {
                    'fields': (
                        'meta_title', 'meta_description', 'meta_keywords',
                        'meta_title_kk', 'meta_description_kk', 'meta_keywords_kk',
                        'meta_title_en', 'meta_description_en', 'meta_keywords_en',
                    ),
                    'classes': ('collapse',)
                }),
                ('Статистика', {
                    'fields': ('views_count', 'created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        else:  # Создание - без превью
            return (
                ('Русский', {
                    'fields': ('title', 'slug', 'category', 'short_description')
                }),
                ('Қазақша', {
                    'fields': ('title_kk', 'short_description_kk', 'description_kk')
                }),
                ('English', {
                    'fields': ('title_en', 'short_description_en', 'description_en')
                }),
                ('Полное описание', {
                    'fields': ('description',)
                }),
                ('Медиа', {
                    'fields': ('image', 'gallery')
                }),
                ('Финансы', {
                    'fields': ('investment_amount', 'currency', 'expected_roi', 'partners', 'partners_kk', 'partners_en')
                }),
                ('Сроки и локация', {
                    'fields': (
                        'start_date', 'end_date',
                        'location', 'location_kk', 'location_en',
                        'country', 'country_kk', 'country_en',
                    )
                }),
                ('Статус', {
                    'fields': ('status', 'is_published', 'is_featured', 'published_date')
                }),
                ('SEO', {
                    'fields': (
                        'meta_title', 'meta_description', 'meta_keywords',
                        'meta_title_kk', 'meta_description_kk', 'meta_keywords_kk',
                        'meta_title_en', 'meta_description_en', 'meta_keywords_en',
                    ),
                    'classes': ('collapse',)
                }),
            )

    def published_status_icon(self, obj):
        """Отображение статуса публикации с иконкой"""
        if obj.is_published:
            return mark_safe('<i class="fas fa-check-circle" style="color: #28a745; font-size: 16px;"></i>')
        return mark_safe('<i class="fas fa-times-circle" style="color: #dc3545; font-size: 16px;"></i>')
    published_status_icon.short_description = 'Опубликовано'

    def featured_icon(self, obj):
        """Отображение избранности с иконкой"""
        if obj.is_featured:
            return mark_safe('<i class="fas fa-star" style="color: #ffc107; font-size: 16px;"></i>')
        return mark_safe('<i class="far fa-star" style="color: #6c757d; font-size: 16px;"></i>')
    featured_icon.short_description = 'Избранный'

    def status_badge(self, obj):
        """Цветной badge для статуса проекта"""
        colors = {
            'planning': '#007bff',
            'active': '#28a745',
            'completed': '#6c757d',
            'suspended': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус'

    def investment_display(self, obj):
        """Форматированное отображение суммы инвестиций"""
        if obj.investment_amount:
            return f'{obj.investment_amount:,.0f} {obj.currency}'
        return '-'
    investment_display.short_description = 'Инвестиции'

    def image_preview(self, obj):
        """Превью изображения"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 200px; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Превью'

    actions = ['publish_projects', 'unpublish_projects', 'feature_projects', 'unfeature_projects']

    def publish_projects(self, request, queryset):
        """Опубликовать выбранные проекты"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'Опубликовано проектов: {updated}')
    publish_projects.short_description = 'Опубликовать выбранные проекты'

    def unpublish_projects(self, request, queryset):
        """Снять с публикации выбранные проекты"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'Снято с публикации проектов: {updated}')
    unpublish_projects.short_description = 'Снять с публикации'

    def feature_projects(self, request, queryset):
        """Сделать проекты избранными"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'Отмечено избранными: {updated}')
    feature_projects.short_description = 'Сделать избранными'

    def unfeature_projects(self, request, queryset):
        """Убрать из избранных"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'Убрано из избранных: {updated}')
    unfeature_projects.short_description = 'Убрать из избранных'
