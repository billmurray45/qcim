from django.contrib import admin
from django.utils.html import format_html
from .models import TeamMember, TeamMemberBioSection, TeamMemberBioItem


class TeamMemberBioItemInline(admin.TabularInline):
    model = TeamMemberBioItem
    extra = 1
    fields = ('text', 'order')


class TeamMemberBioSectionInline(admin.StackedInline):
    model = TeamMemberBioSection
    extra = 1
    fields = ('title', 'order')
    show_change_link = True


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('photo_preview', 'get_full_name', 'position', 'group', 'is_active', 'order')
    list_filter = ('group', 'is_active')
    list_editable = ('order',)
    search_fields = ('last_name', 'first_name', 'position')
    inlines = [TeamMemberBioSectionInline]

    fieldsets = (
        (None, {
            'fields': ('last_name', 'first_name', 'middle_name', 'position', 'group')
        }),
        ('Фото', {
            'fields': ('photo', 'photo_preview_large'),
        }),
        ('Дополнительно', {
            'fields': ('citizenship', 'is_active', 'order')
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


@admin.register(TeamMemberBioSection)
class TeamMemberBioSectionAdmin(admin.ModelAdmin):
    list_display = ('member', 'title', 'order')
    inlines = [TeamMemberBioItemInline]
