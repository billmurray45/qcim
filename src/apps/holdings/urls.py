from django.urls import path
from .views import FundsPageView

app_name = 'holdings'

urlpatterns = [
    path('', FundsPageView.as_view(), name='funds'),
]
