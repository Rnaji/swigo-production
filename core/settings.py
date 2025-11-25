"""
Django settings for core project.
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Charger le .env
load_dotenv()

# BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# Debug pour vérif (uniquement dev)
if 'runserver' in sys.argv or 'test' in sys.argv:
    print("SECRET_KEY loaded:", bool(os.getenv('SECRET_KEY')))
    print("STRIPE_SECRET_KEY loaded:", bool(os.getenv('STRIPE_SECRET_KEY')))

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''  # put here your gmail
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = [
    'app.enroutechef.com',
    'enroutechef.com',
    'www.enroutechef.com',
    '134.209.244.129',
    'localhost',
    '127.0.0.1'
]

# Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'swigo.apps.SwigoConfig',
    'django_extensions',
    'parler',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'package' / 'templates' / 'swigo',
            BASE_DIR / 'package' / 'templates' / 'assets',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://app.enroutechef.com',
    'https://enroutechef.com',
    'https://www.enroutechef.com',
    'http://localhost:8025',
    'http://127.0.0.1:8025',
]

# Dev security
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Password
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# i18n
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'package' / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Stripe
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = 'pk_test_51Q4fHlEnEVSBT8EnzYXw9Vtm54DX1IzljI7Gg8TeuIEHCxmMDpfCPRuJv1GTG1IKWgycUAiNnvJjSKeG00wBhPsX00uZOFs6P2'
STRIPE_WEBHOOK_SECRET = 'whsec_38cdd1b4bfef99b43cd11859a11deb415b2e1d6c2a31fb91a2c350c13de5488a'

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'level': 'DEBUG'},
        'file': {'class': 'logging.FileHandler', 'filename': 'debug.log', 'level': 'DEBUG', 'formatter': 'detailed'},
    },
    'formatters': {
        'detailed': {'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO'},
        'swigo': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': True},
    },
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}

# Parler
PARLER_LANGUAGES = {
    None: (
        {"code": "fr"},
        {"code": "en"},
        {"code": "ar"},
    ),
    "default": {
        "fallback": "fr",
        "hide_untranslated": False,
    }
}


# Dans settings.py
BASE_URL = "http://localhost:8025"  # pour le développement
# ou
BASE_URL = "https://app.enroutechef.com"  # pour la production
