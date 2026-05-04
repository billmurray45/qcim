from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('submit-request/', views.SubmitRequestView.as_view(), name='submit_request'),
    path('privacy-notice/', TemplateView.as_view(template_name='core/privacy_notice.html'), name='privacy_notice'),
    path('anti-corruption/', TemplateView.as_view(template_name='core/anti_corruption.html'), name='anti_corruption'),
    path('disclaimers/', TemplateView.as_view(template_name='core/disclaimers.html'), name='disclaimers'),
]
