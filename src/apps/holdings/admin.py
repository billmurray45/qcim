from django.contrib import admin
from .models import Fund, FundGoal


class FundGoalInline(admin.TabularInline):
    model = FundGoal
    extra = 1
    fields = ('text', 'order')


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge', 'target_size', 'lifespan', 'registration_date', 'is_dark', 'is_active', 'order')
    list_filter = ('is_active', 'is_dark')
    list_editable = ('order',)
    search_fields = ('name', 'badge', 'fund_type')
    inlines = [FundGoalInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'badge', 'fund_type', 'is_active', 'is_dark', 'order')
        }),
        ('Параметры фонда', {
            'fields': ('target_size', 'lifespan', 'registration_date')
        }),
    )
