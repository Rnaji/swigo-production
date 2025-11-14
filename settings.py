"""
Django settings for core project.
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Charger le .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Debug pour vérifier (uniquement en développement)
if 'runserver' in sys.argv or 'test' in sys.argv:
    print("SECRET_KEY loaded:", bool(os.getenv('SECRET_KEY')))
    print("STRIPE_SECRET_KEY loaded:", bool(os.getenv('STRIPE_SECRET_KEY')))

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'noreply.enroutechef@gmail.com'  # ← METTEZ VOTRE EMAIL RÉEL
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply.enroutechef@gmail.com'  # ← LE MÊME QUE EMAIL_HOST_USER


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # ← LIRE DEPUIS .env

ALLOWED_HOSTS = [
    'app.enroutechef.com', 
    'enroutechef.com',
    'www.enroutechef.com',
    '134.209.244.129', 
    'localhost',
    '127.0.0.1'
]

# Application definition
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

# Database - SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CSRF_TRUSTED_ORIGINS = [
    'https://app.enroutechef.com',
    'https://enroutechef.com',
    'https://www.enroutechef.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Security settings - ACTIVER POUR LA PRODUCTION
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    # Désactiver la sécurité en développement
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

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

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'package' / 'static',
]

# Ajouter le dossier package/static seulement s'il existe
package_static_path = BASE_DIR / 'package' / 'static'
if package_static_path.exists():
    STATICFILES_DIRS.append(package_static_path)
    
# Configuration WhiteNoise pour les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Stripe Configuration - PRODUCTION
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')  # ← PLUS EN DUR !
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')    # ← PLUS EN DUR !

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyChxLP7_um9XUuGA3rHlUPTQuB7SRFuSNk')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'file_debug': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',  # ← CHEMIN ABSOLU
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file_errors': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'file_stripe': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'stripe.log',
            'formatter': 'verbose',
            'level': 'INFO',
        },
    },
    
    'loggers': {
        'django': {
            'handlers': ['console', 'file_errors'],
            'level': 'INFO',
            'propagate': False,
        },
        'swigo': {
            'handlers': ['console', 'file_debug', 'file_stripe'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'stripe': {
            'handlers': ['file_stripe', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Parler (multilinguisme)
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