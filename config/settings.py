"""
Django settings for config project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_REDIRECT_URL = '/'

SECRET_KEY = 'django-insecure-*w_+j%%01g-1768ucg8a6q(*(sx#im+4s)r#-tw9@s*-vs4%n4'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'main' / 'templates',
            BASE_DIR / 'main' / 'styles',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
'''
# ========== STATIC FILES ==========
STATIC_URL = '/static/'

# STATICFILES_DIRS — только для разработки (не используется в production)
STATICFILES_DIRS = [
    BASE_DIR / 'main' / 'static',
]
'''
STATIC_ROOT = BASE_DIR / 'staticfiles'

# STATIC_ROOT — куда собираются файлы при collectstatic
# Используем другую папку, чтобы не было конфликта
STATIC_ROOT = BASE_DIR / 'static_collected'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ========== LOGGING ==========
LOG_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} - {message}',
            'style': '{',
        },
        'moderation': {
            'format': '{levelname} {asctime} | User:{user} | Action:{action} | Target:{target} | Reason:{reason} | {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'formatter': 'verbose',
        },
        'file_warnings': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'warnings.log'),
            'formatter': 'verbose',
        },
        'file_moderation': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'moderation.log'),
            'formatter': 'moderation',
        },
        'file_ai': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'ai.log'),
            'formatter': 'simple',
        },
        'file_auth': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'auth.log'),
            'formatter': 'simple',
        },
        'file_db': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'db.log'),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['console', 'file_errors', 'file_warnings'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'main.moderation': {
            'handlers': ['file_moderation', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'main.ai': {
            'handlers': ['file_ai', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'main.auth': {
            'handlers': ['file_auth', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'main.db': {
            'handlers': ['file_db'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}