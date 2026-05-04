import logging
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .models import CustomUser

# Логгер для модуля users
logger = logging.getLogger('apps.users')


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin for CustomUser model.
    """
    list_display = (
        'email',
        'first_name',
        'last_name',
        'role',
        'position',
        'staff_status_icon',
        'active_status_icon',
        'date_joined',
    )
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone', 'position')
    ordering = ('-date_joined',)

    def staff_status_icon(self, obj):
        """Отображение статуса персонала с иконкой"""
        if obj.is_staff:
            return mark_safe('<i class="fas fa-check-circle" style="color: #28a745; font-size: 16px;"></i>')
        return mark_safe('<i class="fas fa-times-circle" style="color: #dc3545; font-size: 16px;"></i>')
    staff_status_icon.short_description = 'Статус персонала'

    def active_status_icon(self, obj):
        """Отображение активности с иконкой"""
        if obj.is_active:
            return mark_safe('<i class="fas fa-check-circle" style="color: #28a745; font-size: 16px;"></i>')
        return mark_safe('<i class="fas fa-times-circle" style="color: #dc3545; font-size: 16px;"></i>')
    active_status_icon.short_description = 'Активен'

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Личная информация'), {
            'fields': ('first_name', 'last_name', 'phone', 'position')
        }),
        (_('Права и роль'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'role',
                'is_staff',
                'is_active',
            ),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')

    def get_readonly_fields(self, request, obj=None):
        """
        Make date_joined and last_login readonly.
        """
        if obj:
            return self.readonly_fields + ('email',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """
        Логирование создания и изменения пользователей через админку.
        """
        if change:
            # Изменение существующего пользователя
            logger.info(
                f'Администратор {request.user.email} изменил пользователя: '
                f'user_id={obj.id}, email={obj.email}'
            )
        else:
            # Создание нового пользователя
            logger.info(
                f'Администратор {request.user.email} создал нового пользователя: '
                f'email={obj.email}, role={obj.role}'
            )

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Логирование удаления пользователей через админку.
        """
        logger.warning(
            f'Администратор {request.user.email} удалил пользователя: '
            f'user_id={obj.id}, email={obj.email}'
        )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Логирование массового удаления пользователей.
        """
        user_emails = list(queryset.values_list('email', flat=True))
        logger.warning(
            f'Администратор {request.user.email} массово удалил пользователей: '
            f'count={queryset.count()}, emails={user_emails}'
        )
        super().delete_queryset(request, queryset)
