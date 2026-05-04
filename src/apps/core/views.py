from django.shortcuts import render
from django.views.generic import TemplateView
from apps.news.models import News
from apps.contacts.models import Office
from .models import TeamMember


class SubmitRequestView(TemplateView):
    template_name = 'core/submit_request.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оставить заявку'
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
        'title': 'Главная страница',
        'latest_news': latest_news,
        'main_office': main_office,
        'team_management': team_management,
        'team_board': team_board,
    }
    return render(request, 'core/home.html', context)
