import logging
from django.views.generic import TemplateView
from .models import Fund

logger = logging.getLogger('apps.holdings')


class FundsPageView(TemplateView):
    template_name = 'holdings/funds_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['funds'] = Fund.objects.filter(is_active=True).prefetch_related('goals')
        logger.info('Просмотр страницы "Наши фонды"')
        return context
