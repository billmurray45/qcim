"""
URL configuration for project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include

from apps.core.views import robots_txt
from apps.news.sitemaps import NewsSitemap, NewsCategorySitemap
from apps.projects.sitemaps import ProjectSitemap, ProjectCategorySitemap
from apps.common.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'news': NewsSitemap,
    'news-categories': NewsCategorySitemap,
    'projects': ProjectSitemap,
    'project-categories': ProjectCategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('auth/', include('apps.users.urls')),
    path('contact/', include('apps.contacts.urls')),
    path('news/', include('apps.news.urls')),
    path('projects/', include('apps.projects.urls')),
    path('funds/', include('apps.holdings.urls')),
    path('', include('apps.core.urls')),
    prefix_default_language=False,
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
