"""
Конфигурация системы логирования для проекта.

Структура логов:
- general.log: Общие логи приложения
- users.log: Логи модуля пользователей (аутентификация, регистрация, профили)
- errors.log: Все ошибки (ERROR и выше)
- security.log: Логи безопасности (неудачные попытки входа, подозрительная активность)
"""

from pathlib import Path

# Путь к корневой директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Путь к директории логов
LOGS_DIR = BASE_DIR.parent / 'var' / 'logs'

# Создаем директорию для логов, если её нет
LOGS_DIR.mkdir(exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    # Форматтеры - определяют формат сообщений в логах
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} | {name} | {module}.{funcName}:{lineno} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    # Фильтры
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    # Handlers - определяют куда отправлять логи
    'handlers': {
        # Консоль (для разработки)
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },

        # Общий лог файл
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'general.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # Лог файл для модуля пользователей
        'file_users': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'users.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # Лог файл только для ошибок
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,  # Храним больше файлов с ошибками
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # Лог файл для безопасности
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # Лог файл для модуля контактов
        'file_contacts': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'contacts.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },

        # Email для критических ошибок (опционально)
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },

    # Логгеры - определяют какие модули логировать и куда
    'loggers': {
        # Django система
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },

        # Django запросы (500 ошибки и т.д.)
        'django.request': {
            'handlers': ['file_errors', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },

        # Django безопасность
        'django.security': {
            'handlers': ['file_security'],
            'level': 'WARNING',
            'propagate': False,
        },

        # Модуль пользователей
        'apps.users': {
            'handlers': ['console', 'file_users', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },

        # Модуль core
        'apps.core': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },

        # Модуль news
        'apps.news': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },

        # Модуль projects
        'apps.projects': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': False,
        },

        # Модуль contacts
        'apps.contacts': {
            'handlers': ['console', 'file_contacts', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },

        # Логгер безопасности (кастомный)
        'security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },

        # Django Axes - защита от brute-force
        'axes.watch_login': {
            'handlers': ['console', 'file_security', 'file_users'],
            'level': 'WARNING',
            'propagate': False,
        },
    },

    # Root logger (по умолчанию)
    'root': {
        'handlers': ['console', 'file_general'],
        'level': 'INFO',
    },
}
