from django.contrib.sitemaps import Sitemap
from .models import Project, ProjectCategory


class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProjectCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.4

    def items(self):
        return ProjectCategory.objects.filter(is_active=True)

    def location(self, obj):
        from django.urls import reverse
        return reverse('projects:category', kwargs={'slug': obj.slug})
