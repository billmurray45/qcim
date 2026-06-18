from django.contrib.sitemaps import Sitemap
from .models import News, Category


class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return News.objects.filter(is_published=True).order_by('-published_date')

    def lastmod(self, obj):
        return obj.updated_at


class NewsCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.4

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        from django.urls import reverse
        return reverse('news:category', kwargs={'slug': obj.slug})
