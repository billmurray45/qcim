from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from apps.news.models import News
from apps.contacts.models import Office
from .models import TeamMember


def robots_txt(request):
    if settings.DEBUG:
        content = 'User-agent: *\nDisallow: /\n'
    else:
        sitemap_url = request.build_absolute_uri('/sitemap.xml')
        content = (
            'User-agent: *\n'
            'Disallow: /admin/\n'
            'Disallow: /auth/\n'
            'Disallow: /ckeditor5/\n'
            f'Sitemap: {sitemap_url}\n'
        )
    return HttpResponse(content, content_type='text/plain')


class SubmitRequestView(TemplateView):
    template_name = 'core/submit_request.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Оставить заявку')
        return context


def home_page(request):
    latest_news = News.objects.filter(
        is_published=True
    ).select_related('category').order_by('-published_date')[:3]

    main_office = Office.objects.filter(is_main=True, is_active=True).first()

    team_management = TeamMember.objects.filter(
        is_active=True, group=TeamMember.Group.MANAGEMENT
    ).prefetch_related('bio_sections__items')

    team_board = TeamMember.objects.filter(
        is_active=True, group=TeamMember.Group.BOARD
    ).prefetch_related('bio_sections__items')

    context = {
        'title': _('Главная страница'),
        'latest_news': latest_news,
        'main_office': main_office,
        'team_management': team_management,
        'team_board': team_board,
    }
    return render(request, 'core/home.html', context)
