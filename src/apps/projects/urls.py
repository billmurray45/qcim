from django.urls import path
from .views import ProjectListView, ProjectDetailView, CategoryProjectsView

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('category/<slug:slug>/', CategoryProjectsView.as_view(), name='category'),
    path('<slug:slug>/', ProjectDetailView.as_view(), name='detail'),
]
