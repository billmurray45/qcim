import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from .forms import ContactForm
from .models import Office
from apps.common.utils import get_client_ip

# Логгеры
logger = logging.getLogger('apps.contacts')
security_logger = logging.getLogger('security')


def get_user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')


def send_contact_email(contact_message):
    """
    Отправка email уведомления о новом сообщении из формы обратной связи.
    """
    try:
        subject = f'Новое сообщение: {contact_message.get_subject_display()}'

        # Формируем тело письма
        message_body = f"""
Получено новое сообщение через форму обратной связи.

Имя: {contact_message.name}
Email: {contact_message.email}
Телефон: {contact_message.phone}
Тема: {contact_message.get_subject_display()}

Сообщение:
{contact_message.message}

---
Дата: {contact_message.created_at.strftime('%d.%m.%Y %H:%M')}
IP адрес: {contact_message.ip_address or 'Неизвестен'}
"""

        # Отправляем email
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.CONTACT_EMAIL_RECIPIENTS,
            fail_silently=False,
        )

        logger.info(
            f'Email уведомление отправлено для сообщения от {contact_message.name} '
            f'({contact_message.email})'
        )
        return True

    except Exception as e:
        logger.error(
            f'Ошибка при отправке email для сообщения от {contact_message.name}: {str(e)}'
        )
        return False


@require_http_methods(["POST"])
def contact_submit(request):
    """
    Обработка формы обратной связи.
    Поддерживает как обычную отправку формы, так и AJAX.
    Доступно всем пользователям, включая неавторизованных.
    """
    form = ContactForm(request.POST)

    # Получаем метаданные
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Проверяем, это AJAX запрос или обычная форма
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.headers.get('Accept', '').find('application/json') != -1
    )

    if form.is_valid():
        # Сохраняем сообщение с метаданными
        contact_message = form.save(
            commit=False,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        contact_message.save()

        # Логируем успешную отправку
        logger.info(
            f'Новое сообщение от {contact_message.name} '
            f'(email: {contact_message.email}, '
            f'тема: {contact_message.get_subject_display()}, '
            f'IP: {ip_address})'
        )

        # Отправляем email уведомление
        send_contact_email(contact_message)

        # Формируем ответ
        success_message = _('Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.')

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': str(success_message)
            })
        else:
            messages.success(request, success_message)
            return redirect('contacts:page')

    else:
        # Логируем ошибку валидации
        error_details = ', '.join([f'{field}: {errors}' for field, errors in form.errors.items()])
        logger.warning(
            f'Ошибка валидации формы обратной связи: {error_details} '
            f'(IP: {ip_address})'
        )

        # Проверка на подозрительную активность (много ошибок с одного IP)
        if len(form.errors) > 5:
            security_logger.warning(
                f'Подозрительная активность: множественные ошибки валидации '
                f'формы обратной связи с IP: {ip_address}'
            )

        if is_ajax:
            # Формируем детальные ошибки для AJAX
            errors_dict = {}
            for field, errors in form.errors.items():
                errors_dict[field] = [str(error) for error in errors]

            return JsonResponse({
                'success': False,
                'errors': errors_dict,
                'message': _('Пожалуйста, исправьте ошибки в форме.')
            }, status=400)
        else:
            # Для обычной формы добавляем общее сообщение об ошибке
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))

            # Добавляем детальные ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

            return redirect('contacts:page')


class ContactPageView(TemplateView):
    """
    Страница контактов с информацией об офисах и формой обратной связи.
    """
    template_name = 'contacts/contact_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем все активные офисы
        offices = Office.objects.filter(is_active=True).order_by('order', 'city')

        # Получаем главный офис отдельно
        main_office = offices.filter(is_main=True).first()

        # Получаем остальные офисы
        other_offices = offices.filter(is_main=False)

        context['main_office'] = main_office
        context['offices'] = other_offices
        context['form'] = ContactForm()

        return context
