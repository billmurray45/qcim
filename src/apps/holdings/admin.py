from django.contrib import admin
from .models import Fund, FundGoal


class FundGoalInline(admin.TabularInline):
    model = FundGoal
    extra = 1
    fields = ('text', 'text_kk', 'text_en', 'order')


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge', 'target_size', 'lifespan', 'registration_date', 'is_dark', 'is_active', 'order')
    list_filter = ('is_active', 'is_dark')
    list_editable = ('order',)
    search_fields = (
        'name', 'badge', 'fund_type',
        'name_kk', 'badge_kk', 'fund_type_kk',
        'name_en', 'badge_en', 'fund_type_en',
    )
    inlines = [FundGoalInline]

    fieldsets = (
        ('Русский', {
            'fields': ('name', 'badge', 'fund_type', 'is_active', 'is_dark', 'order')
        }),
        ('Қазақша', {
            'fields': ('name_kk', 'badge_kk', 'fund_type_kk')
        }),
        ('English', {
            'fields': ('name_en', 'badge_en', 'fund_type_en')
        }),
        ('Параметры фонда', {
            'fields': (
                'target_size', 'target_size_kk', 'target_size_en',
                'lifespan', 'lifespan_kk', 'lifespan_en',
                'registration_date',
            )
        }),
    )
