from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return [
            ('core:home', 1.0),
            ('holdings:funds', 0.8),
            ('news:list', 0.7),
            ('projects:list', 0.7),
            ('contacts:page', 0.5),
            ('core:privacy_notice', 0.3),
            ('core:anti_corruption', 0.3),
            ('core:disclaimers', 0.3),
        ]

    def location(self, item):
        url_name, _priority = item
        return reverse(url_name)

    def priority(self, item):
        _url_name, priority = item
        return priority
