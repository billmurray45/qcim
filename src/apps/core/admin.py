import nested_admin
from django.contrib import admin
from django.utils.html import format_html
from .models import TeamMember, TeamMemberBioSection, TeamMemberBioItem


class TeamMemberBioItemInline(nested_admin.NestedTabularInline):
    model = TeamMemberBioItem
    extra = 1
    fields = ('text', 'text_kk', 'text_en', 'order')


class TeamMemberBioSectionInline(nested_admin.NestedStackedInline):
    model = TeamMemberBioSection
    extra = 1
    fields = ('title', 'title_kk', 'title_en', 'order')
    inlines = [TeamMemberBioItemInline]


@admin.register(TeamMember)
class TeamMemberAdmin(nested_admin.NestedModelAdmin):
    list_display = ('photo_preview', 'get_full_name', 'position', 'group', 'is_active', 'order')
    list_filter = ('group', 'is_active')
    list_editable = ('order',)
    search_fields = (
        'last_name', 'first_name', 'position',
        'last_name_kk', 'first_name_kk', 'position_kk',
        'last_name_en', 'first_name_en', 'position_en',
    )
    inlines = [TeamMemberBioSectionInline]

    fieldsets = (
        ('Русский', {
            'fields': ('last_name', 'first_name', 'middle_name', 'position', 'group')
        }),
        ('Қазақша', {
            'fields': ('last_name_kk', 'first_name_kk', 'middle_name_kk', 'position_kk')
        }),
        ('English', {
            'fields': ('last_name_en', 'first_name_en', 'middle_name_en', 'position_en')
        }),
        ('Фото', {
            'fields': ('photo', 'photo_preview_large'),
        }),
        ('Дополнительно', {
            'fields': ('citizenship', 'citizenship_kk', 'citizenship_en', 'is_active', 'order')
        }),
    )
    readonly_fields = ('photo_preview_large',)

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:36px;height:36px;object-fit:cover;border-radius:50%;" />',
                obj.photo.url
            )
        return '—'
    photo_preview.short_description = 'Фото'

    def photo_preview_large(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:200px;max-height:200px;object-fit:cover;border-radius:8px;" />',
                obj.photo.url
            )
        return 'Фото не загружено'
    photo_preview_large.short_description = 'Текущее фото'
