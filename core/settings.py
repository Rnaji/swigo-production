"""
Django settings for core project.
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Charger la configuration environnement
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
    print("🔧 Chargement .env.local (DÉVELOPPEMENT)")
else:
    load_dotenv('.env.production')
    print("🚀 Chargement .env.production (PRODUCTION)")

# BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# Debug pour vérif (uniquement dev)
if 'runserver' in sys.argv:
    print("=" * 50)
    print("🔍 CONFIGURATION DJANGO")
    print("=" * 50)

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

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

# Security configuration
if DEBUG:
    # Mode développement
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    # Mode production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

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

# 🔥 SOLUTION DÉFINITIVE - Stripe Configuration
if DEBUG:
    # MODE DÉVELOPPEMENT - Clés TEST FORCÉES DIRECTEMENT
    STRIPE_SECRET_KEY = "sk_test_51Q4fHlEnEVSBT8En6GJbcTL7O6vGqBJhRna2SNvQJbaF1peU1Mx2eeirZTWFufTwcVl6bbG08saRXD9uG5bUXZT400Poc4UFGZ"
    STRIPE_PUBLISHABLE_KEY = "pk_test_51Q4fHlEnEVSBT8EnWVflBcZGmQ7r0HOYV95ItdV4St4BSL7ZNpx86KQA0OLQ8VZHIcWlgYox2i7pBdFn05kMzGT800KmFmRSic"
    STRIPE_WEBHOOK_SECRET = "whsec_38cdd1b4bfef99b43cd11859a11deb415b2e1d6c2a31fb91a2c350c13de5488a"
    STRIPE_MODE = "TEST"
    print("🔧 Clés Stripe TEST forcées directement dans le code")
else:
    # MODE PRODUCTION - Utiliser les variables d'environnement
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_MODE = "PRODUCTION"
    print("🚀 Mode Stripe PRODUCTION")

# Vérification de sécurité
if DEBUG and STRIPE_SECRET_KEY and STRIPE_SECRET_KEY.startswith('sk_live'):
    print("❌ ⚠️  ATTENTION: Clés Stripe PRODUCTION en mode DÉVELOPPEMENT!")

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'enroutechef@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Base URL configuration
if DEBUG:
    BASE_URL = "http://localhost:8000"
else:
    BASE_URL = "https://app.enroutechef.com"

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

# Vérification au démarrage serveur
if 'runserver' in sys.argv:
    print(f"📝 Environnement: {'🔧 DÉVELOPPEMENT' if DEBUG else '🚀 PRODUCTION'}")
    print(f"📝 DEBUG: {DEBUG}")
    print(f"📝 Stripe Mode: {STRIPE_MODE}")
    print(f"📝 Stripe Secret Key: {'✅ Chargée' if STRIPE_SECRET_KEY else '❌ Manquante'}")
    print(f"📝 Stripe Publishable Key: {'✅ Chargée' if STRIPE_PUBLISHABLE_KEY else '❌ Manquante'}")
    print(f"📝 Stripe Webhook Secret: {'✅ Chargée' if STRIPE_WEBHOOK_SECRET else '❌ Manquante'}")
    
    # Afficher le préfixe des clés pour vérification
    if STRIPE_SECRET_KEY:
        prefix = STRIPE_SECRET_KEY[:7]
        detected_mode = "TEST" if prefix == "sk_test" else "PRODUCTION"
        print(f"📝 Type de clé détecté: {detected_mode} ({prefix}...)")
    
    print(f"📝 BASE_URL: {BASE_URL}")
    print(f"📝 EMAIL_HOST_USER: {'✅ Configuré' if EMAIL_HOST_USER else '❌ Manquant'}")
    print(f"📝 GOOGLE_MAPS_API_KEY: {'✅ Chargée' if GOOGLE_MAPS_API_KEY else '❌ Manquante'}")
    print("=" * 50)

# Vérifications de sécurité en production
if not DEBUG and 'runserver' in sys.argv:
    print("🔒 VÉRIFICATIONS SÉCURITÉ PRODUCTION:")
    
    # Vérifier que les clés de production sont bien utilisées
    if STRIPE_SECRET_KEY and STRIPE_SECRET_KEY.startswith('sk_test'):
        print("❌ ATTENTION: Clé Stripe TEST détectée en mode PRODUCTION!")
    
    if not SECURE_SSL_REDIRECT:
        print("❌ ATTENTION: SECURE_SSL_REDIRECT désactivé en production!")
    
    if not all([SECRET_KEY, STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY]):
        print("❌ ATTENTION: Clés sensibles manquantes en production!")
    
    print("✅ Vérifications sécurité terminées")
    print("=" * 50)