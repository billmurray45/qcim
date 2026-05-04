import logging
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import News, Category, ExternalNews

logger = logging.getLogger('apps.news')


class NewsListView(ListView):
    """Список всех новостей с пагинацией"""
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 9

    def get_queryset(self):
        queryset = News.objects.filter(
            is_published=True
        ).select_related('category').order_by('-published_date')

        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('q', '')
        context['baiterek_news'] = ExternalNews.objects.filter(
            source=ExternalNews.SOURCE_BAITEREK
        ).order_by('-published_date')[:6]
        context['qic_news'] = ExternalNews.objects.filter(
            source=ExternalNews.SOURCE_QIC
        ).order_by('-published_date')[:6]
        context['active_tab'] = self.request.GET.get('tab', 'own')
        return context


class NewsDetailView(DetailView):
    """Детальная страница новости"""
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return News.objects.filter(is_published=True).select_related('category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.increment_views()
        logger.info(f'Просмотр новости: {obj.title} (ID: {obj.id})')
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем связанные новости
        news = self.object
        related_news = News.objects.filter(
            is_published=True
        ).exclude(id=news.id)

        if news.category:
            related_news = related_news.filter(category=news.category)

        context['related_news'] = related_news.select_related('category')[:3]
        return context


class CategoryNewsView(ListView):
    """Список новостей по категории"""
    model = News
    template_name = 'news/category_news.html'
    context_object_name = 'news_list'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_active=True
        )
        return News.objects.filter(
            category=self.category,
            is_published=True
        ).select_related('category').order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True)
        return context
