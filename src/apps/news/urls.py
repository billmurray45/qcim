from django.urls import path
from .views import NewsListView, NewsDetailView, CategoryNewsView

app_name = 'news'

urlpatterns = [
    path('', NewsListView.as_view(), name='list'),
    path('category/<slug:slug>/', CategoryNewsView.as_view(), name='category'),
    path('<slug:slug>/', NewsDetailView.as_view(), name='detail'),
]
