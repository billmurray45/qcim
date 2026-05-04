from django.urls import path

from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.ContactPageView.as_view(), name='page'),
    path('submit/', views.contact_submit, name='submit'),
]
