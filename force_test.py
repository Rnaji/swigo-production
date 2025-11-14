import os
import sys
import django

# Force un rechargement complet
if 'django.conf' in sys.modules:
    del sys.modules['django.conf']
if 'core.settings' in sys.modules:
    del sys.modules['core.settings']

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
print("=== FORCED RELOAD ===")
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('DEBUG:', settings.DEBUG)
print('SECRET_KEY défini:', bool(settings.SECRET_KEY))
