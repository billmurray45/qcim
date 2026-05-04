import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import CustomUser
from apps.common.utils import get_client_ip

logger = logging.getLogger('apps.users')
security_logger = logging.getLogger('security')


@require_http_methods(["POST"])
def login_view(request):
    """
    Обработка входа пользователя в систему.

    Логирует успешные и неудачные попытки входа.
    """
    email = request.POST.get('email')
    password = request.POST.get('password')
    client_ip = get_client_ip(request)

    logger.info(f'Попытка входа: email={email}, IP={client_ip}')

    user = authenticate(request, email=email, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, 'Вы успешно вошли в систему!')

        # Логируем успешный вход
        logger.info(
            f'Успешный вход: user_id={user.id}, email={user.email}, '
            f'name={user.get_full_name()}, IP={client_ip}'
        )

        return JsonResponse({
            'success': True,
            'message': 'Вы успешно вошли в систему!'
        })
    else:
        security_logger.warning(
            f'Неудачная попытка входа: email={email}, IP={client_ip}'
        )

        logger.warning(f'Неудачная попытка входа: email={email}, IP={client_ip}')

        return JsonResponse({
            'success': False,
            'error': 'Неверный email или пароль.'
        })


@require_http_methods(["POST"])
def logout_view(request):
    """
    Обработка выхода пользователя из системы.

    Логирует выход пользователя.
    """
    client_ip = get_client_ip(request)

    if request.user.is_authenticated:
        user_email = request.user.email
        user_id = request.user.id

        logout(request)
        messages.success(request, 'Вы вышли из системы.')

        # Логируем выход
        logger.info(
            f'Выход из системы: user_id={user_id}, email={user_email}, IP={client_ip}'
        )
    else:
        # Попытка выйти без авторизации
        logger.warning(f'Попытка выхода неавторизованного пользователя: IP={client_ip}')
        logout(request)

    return redirect('core:home')


@require_http_methods(["POST"])
def register_view(request):
    """
    Обработка регистрации нового пользователя.

    Валидирует данные, создаёт пользователя и автоматически авторизует.
    """
    client_ip = get_client_ip(request)

    # Получаем данные из формы
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    phone = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')
    agree = request.POST.get('agree')

    errors = {}

    # Валидация имени
    if not first_name:
        errors['first_name'] = 'Введите имя'
    elif len(first_name) < 2:
        errors['first_name'] = 'Имя слишком короткое'

    # Валидация фамилии
    if not last_name:
        errors['last_name'] = 'Введите фамилию'
    elif len(last_name) < 2:
        errors['last_name'] = 'Фамилия слишком короткая'

    # Валидация email
    if not email:
        errors['email'] = 'Введите email'
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Некорректный email адрес'
        else:
            # Проверяем, не занят ли email
            if CustomUser.objects.filter(email=email).exists():
                errors['email'] = 'Пользователь с таким email уже существует'

    # Валидация пароля
    if not password:
        errors['password'] = 'Введите пароль'
    elif len(password) < 8:
        errors['password'] = 'Пароль должен содержать минимум 8 символов'
    elif password.isdigit():
        errors['password'] = 'Пароль не может состоять только из цифр'

    # Проверка совпадения паролей
    if password != password2:
        errors['password2'] = 'Пароли не совпадают'

    # Проверка согласия
    if not agree:
        errors['agree'] = 'Необходимо принять условия использования'

    # Если есть ошибки — возвращаем их
    if errors:
        logger.warning(f'Ошибка регистрации: email={email}, errors={errors}, IP={client_ip}')
        return JsonResponse({
            'success': False,
            'errors': errors,
            'message': 'Пожалуйста, исправьте ошибки в форме'
        })

    try:
        # Создаём пользователя
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        # Логируем успешную регистрацию
        logger.info(
            f'Успешная регистрация: user_id={user.id}, email={user.email}, '
            f'name={user.get_full_name()}, IP={client_ip}'
        )

        # Автоматически авторизуем пользователя
        # Указываем backend, т.к. пользователь создан напрямую, а не через authenticate()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        messages.success(request, f'Добро пожаловать, {user.first_name}! Регистрация прошла успешно.')

        return JsonResponse({
            'success': True,
            'message': 'Регистрация прошла успешно!'
        })

    except Exception as e:
        logger.error(f'Ошибка при создании пользователя: email={email}, error={str(e)}, IP={client_ip}')
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при регистрации. Попробуйте позже.'
        })


class CabinetView(LoginRequiredMixin, TemplateView):
    """
    Личный кабинет пользователя.
    """
    template_name = 'users/cabinet.html'


