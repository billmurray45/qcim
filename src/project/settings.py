import os

from pathlib import Path
from dotenv import load_dotenv


# Путь к директории с приложением и проектом
BASE_APP_DIR = Path(__file__).resolve().parent.parent
BASE_PROJECT_DIR = BASE_APP_DIR.parent

# Путь к var директории (logs, media, staticfiles)
VAR_DIR = BASE_PROJECT_DIR / 'var'


# Путь к .env файлу
dotenv_path = BASE_PROJECT_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path, encoding="utf-8")


# Секретный ключ
SECRET_KEY = os.getenv("SECRET_KEY")


# Режим отладки
DEBUG = os.getenv('DEBUG', 'False') == 'True'


# Разрешенные хосты
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Доверенные источники для CSRF
_csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]


# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'axes',
    'compressor',
    'htmlmin',

    # Local apps
    'apps.core',
    'apps.users',
    'apps.news',
    'apps.projects',
    'apps.contacts',
    'apps.holdings',
    'apps.common',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
]

HTML_MINIFY = not DEBUG

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_APP_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.main_office',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST", "localhost"),
        "NAME": os.getenv("DB_NAME", "invest_db"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'


# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# Internationalization
LANGUAGE_CODE = 'ru-KZ'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = VAR_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_APP_DIR / 'static',
]


# Django Compressor Settings
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}

COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = False
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.rJSMinFilter',
]


# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = VAR_DIR / 'media'


# Email Configuration
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'  # Default: console for development
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)


# Contact form email settings
CONTACT_EMAIL_RECIPIENTS = os.getenv(
    'CONTACT_EMAIL_RECIPIENTS',
    'admin@example.com'
).split(',')  # Comma-separated list of recipients


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Jazzmin Settings
JAZZMIN_SETTINGS = {
    "site_title": "Invest Admin",
    "site_header": "Investment Capital",
    "site_brand": "Invest CMS",
    "welcome_sign": "Добро пожаловать в панель управления",
    "copyright": "Qazaqstan Investment Capital Management",
    "search_model": "users.CustomUser",
    "user_avatar": None,

    "topmenu_links": [
        {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Сайт", "url": "/", "new_window": True},
    ],

    "usermenu_links": [
        {"model": "users.customuser"}
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["users", "core", "news", "projects"],
    "icons": {
        "auth": "fas fa-users-cog",
        "users.customuser": "fas fa-user",
        "core": "fas fa-home",
        "news": "fas fa-newspaper",
        "projects": "fas fa-project-diagram",
        "contacts": "fas fa-address-book",
        "holdings": "fas fa-building",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"users.customuser": "collapsible", "auth.group": "vertical_tabs"},
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}


# Logging Configuration
from .logging_config import LOGGING  # noqa: E402

AXES_FAILURE_LIMIT = 10  # Попытки входа
AXES_COOLOFF_TIME = 1  # 1 час
AXES_LOCKOUT_PARAMETERS = [['ip_address']]
AXES_ENABLE_ACCESS_FAILURE_LOG = True  # Logging
AXES_NEVER_LOCKOUT_WHITELIST = True  # Не блокировать доступ к админке для суперпользователей

AXES_VERBOSE = True
AXES_LOCKOUT_TEMPLATE = None  # None = стандартное сообщение об ошибке

AXES_RESET_ON_SUCCESS = True  # Сброс попыток входа при успешной аутентификации

AXES_IP_WHITELIST = []

AXES_IP_BLACKLIST = []


# HTTPS Security
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # nginx terminates SSL — trust X-Forwarded-Proto, but don't redirect ourselves
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Заголовки безопасности
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
