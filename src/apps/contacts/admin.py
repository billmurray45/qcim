import logging

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage, Office

logger = logging.getLogger('apps.contacts')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Админка для управления сообщениями из формы обратной связи.
    """

    list_display = [
        'id',
        'name',
        'email',
        'phone',
        'subject_display',
        'status_badge',
        'user_link',
        'created_at_display',
        'ip_address',
    ]

    list_filter = [
        'status',
        'subject',
        'created_at',
        'is_read',
        'is_replied',
    ]

    search_fields = [
        'name',
        'email',
        'phone',
        'message',
        'ip_address',
    ]

    readonly_fields = [
        'created_at',
        'read_at',
        'ip_address',
        'user_agent',
        'message_preview',
    ]

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'email', 'phone', 'subject', 'user')
        }),
        (_('Сообщение'), {
            'fields': ('message', 'message_preview')
        }),
        (_('Статус'), {
            'fields': ('status', 'is_read', 'is_replied', 'read_at')
        }),
        (_('Метаданные'), {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_replied', 'set_status_in_progress']

    def subject_display(self, obj):
        """Отображение темы с иконкой."""
        icons = {
            'investment': '💰',
            'consulting': '💼',
            'partnership': '🤝',
            'other': '📧',
        }
        icon = icons.get(obj.subject, '📧')
        return f'{icon} {obj.get_subject_display()}'
    subject_display.short_description = _('Тема')

    def status_badge(self, obj):
        """Цветной бейдж статуса."""
        status_colors = {
            'new': ('#dc3545', 'white'),  # Красный
            'read': ('#ffc107', 'black'),  # Желтый
            'in_progress': ('#17a2b8', 'white'),  # Синий
            'replied': ('#28a745', 'white'),  # Зеленый
            'cancelled': ('#6c757d', 'white'),  # Серый
        }
        color, text_color = status_colors.get(obj.status, ('#dc3545', 'white'))

        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, text_color, obj.get_status_display()
        )
    status_badge.short_description = _('Статус')

    def user_link(self, obj):
        """Ссылка на пользователя."""
        if obj.user:
            from django.urls import reverse
            url = reverse('admin:users_customuser_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.email)
        return '-'
    user_link.short_description = _('Пользователь')

    def created_at_display(self, obj):
        """Форматированная дата создания."""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    created_at_display.short_description = _('Дата создания')
    created_at_display.admin_order_field = 'created_at'

    def message_preview(self, obj):
        """Превью сообщения."""
        if obj.message:
            preview = obj.message[:200]
            if len(obj.message) > 200:
                preview += '...'
            return format_html('<div style="white-space: pre-wrap;">{}</div>', preview)
        return '-'
    message_preview.short_description = _('Предпросмотр сообщения')

    @admin.action(description=_('Отметить как прочитанное'))
    def mark_as_read(self, request, queryset):
        """Массовая отметка сообщений как прочитанных."""
        count = 0
        for obj in queryset.filter(is_read=False):
            obj.mark_as_read()
            count += 1

        self.message_user(
            request,
            _(f'Отмечено как прочитанное: {count} сообщений.')
        )

        logger.info(
            f'Администратор {request.user.email} отметил {count} сообщений как прочитанные'
        )

    @admin.action(description=_('Отметить как непрочитанное'))
    def mark_as_unread(self, request, queryset):
        """Массовая отметка сообщений как непрочитанных."""
        count = queryset.filter(is_read=True).update(is_read=False, read_at=None)

        self.message_user(
            request,
            _(f'Отмечено как непрочитанное: {count} сообщений.')
        )

        logger.info(
            f'Администратор {request.user.email} отметил {count} сообщений как непрочитанные'
        )

    @admin.action(description=_('Отметить что ответили'))
    def mark_as_replied(self, request, queryset):
        """Массовая отметка что на сообщения ответили."""
        count = 0
        for obj in queryset.filter(is_replied=False):
            obj.mark_as_replied()
            if not obj.is_read:
                obj.mark_as_read()
            count += 1

        self.message_user(
            request,
            _(f'Отмечено что ответили: {count} сообщений.')
        )

        logger.info(
            f'Администратор {request.user.email} отметил {count} сообщений как отвеченные'
        )

    @admin.action(description=_('Перевести в статус "В обработке"'))
    def set_status_in_progress(self, request, queryset):
        """Перевод сообщений в статус 'В обработке'."""
        from .models import ContactMessage
        count = queryset.exclude(
            status__in=[ContactMessage.MessageStatus.REPLIED, ContactMessage.MessageStatus.CANCELLED]
        ).update(status=ContactMessage.MessageStatus.IN_PROGRESS)

        self.message_user(
            request,
            _(f'Переведено в статус "В обработке": {count} сообщений.')
        )

        logger.info(
            f'Администратор {request.user.email} перевел {count} сообщений в статус "В обработке"'
        )

    def save_model(self, request, obj, form, change):
        """Логирование изменений через админку."""
        if change:
            logger.info(
                f'Администратор {request.user.email} изменил сообщение: '
                f'id={obj.id}, от {obj.name} ({obj.email})'
            )
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """Логирование удаления через админку."""
        logger.warning(
            f'Администратор {request.user.email} удалил сообщение: '
            f'id={obj.id}, от {obj.name} ({obj.email})'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Логирование массового удаления."""
        count = queryset.count()
        logger.warning(
            f'Администратор {request.user.email} удалил {count} сообщений'
        )
        super().delete_queryset(request, queryset)


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    """Админка для управления офисами компании."""

    list_display = [
        'city',
        'address',
        'phone',
        'email',
        'active_badge',
        'main_badge',
        'order',
    ]

    list_filter = [
        'is_active',
        'is_main',
        'city',
    ]

    search_fields = [
        'city',
        'city_kk',
        'city_en',
        'address',
        'address_kk',
        'address_en',
        'phone',
        'email',
    ]

    fieldsets = (
        (_('Русский'), {
            'fields': ('city', 'address', 'phone', 'email', 'working_hours')
        }),
        (_('Қазақша'), {
            'fields': ('city_kk', 'address_kk', 'working_hours_kk')
        }),
        (_('English'), {
            'fields': ('city_en', 'address_en', 'working_hours_en')
        }),
        (_('Координаты для карты'), {
            'fields': ('latitude', 'longitude'),
            'description': 'Координаты для отображения офиса на карте'
        }),
        (_('Социальные сети'), {
            'fields': ('instagram', 'facebook', 'linkedin', 'twitter', 'youtube', 'telegram', 'whatsapp', 'tiktok'),
            'classes': ('collapse',),
            'description': 'Ссылки на социальные сети офиса или компании'
        }),
        (_('Настройки'), {
            'fields': ('is_main', 'is_active', 'order')
        }),
    )

    list_editable = ['order']
    list_per_page = 20

    def active_badge(self, obj):
        """Бейдж активности."""
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">{}</span>',
                '✓ Активен'
            )
        return format_html(
            '<span style="color: #dc3545;">{}</span>',
            '✗ Неактивен'
        )
    active_badge.short_description = _('Активность')

    def main_badge(self, obj):
        """Бейдж главного офиса."""
        if obj.is_main:
            return format_html(
                '<span style="background: #ffc107; color: #000; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
                '★ Главный'
            )
        return '-'
    main_badge.short_description = _('Тип')
