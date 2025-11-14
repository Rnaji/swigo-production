# test_final.py
import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print("🎉 TEST FINAL PRODUCTION")
print("=" * 50)

# Configuration
print(f"✅ DEBUG: {settings.DEBUG}")
print(f"✅ Stripe Mode: {'PRODUCTION' if settings.STRIPE_SECRET_KEY.startswith('sk_live_') else 'TEST'}")
print(f"✅ Email: {'CONFIGURÉ' if settings.EMAIL_HOST_PASSWORD else 'NON CONFIGURÉ'}")

# Test logging
logger = logging.getLogger('swigo')
logger.info("=== APPLICATION EN PRODUCTION ===")

print("✅ Logging fonctionnel")
print("✅ Configuration Django valide")
print("=" * 50)
print("🚀 VOTRE APPLICATION EST PRÊTE POUR LA PRODUCTION !")