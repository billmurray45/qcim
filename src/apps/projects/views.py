import logging
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Project, ProjectCategory, ProjectStatus

logger = logging.getLogger('apps.projects')


class ProjectListView(ListView):
    """Список всех инвестиционных проектов с пагинацией"""
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        queryset = Project.objects.filter(
            is_published=True
        ).select_related('category').order_by('-published_date')

        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status and status in dict(ProjectStatus.choices):
            queryset = queryset.filter(status=status)

        # Фильтр по избранным
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)

        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(title_kk__icontains=search_query) |
                Q(title_en__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(description_kk__icontains=search_query) |
                Q(description_en__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(short_description_kk__icontains=search_query) |
                Q(short_description_en__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(location_kk__icontains=search_query) |
                Q(location_en__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProjectCategory.objects.filter(is_active=True)
        context['featured_projects'] = Project.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category')[:3]
        context['search_query'] = self.request.GET.get('q', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['project_statuses'] = ProjectStatus.choices
        return context


class ProjectDetailView(DetailView):
    """Детальная страница проекта"""
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Project.objects.filter(is_published=True).select_related('category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.increment_views()
        logger.info(f'Просмотр проекта: {obj.title} (ID: {obj.id})')
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем похожие проекты
        project = self.object
        related_projects = Project.objects.filter(
            is_published=True
        ).exclude(id=project.id)

        if project.category:
            related_projects = related_projects.filter(category=project.category)

        context['related_projects'] = related_projects.select_related('category')[:3]
        return context


class CategoryProjectsView(ListView):
    """Список проектов по категории"""
    model = Project
    template_name = 'projects/category_projects.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(
            ProjectCategory,
            slug=self.kwargs['slug'],
            is_active=True
        )
        return Project.objects.filter(
            category=self.category,
            is_published=True
        ).select_related('category').order_by('-published_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = ProjectCategory.objects.filter(is_active=True)
        return context
