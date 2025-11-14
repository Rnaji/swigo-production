# confirmation_production.py
import os
import django
import stripe
from dotenv import load_dotenv

load_dotenv('.env.production')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print("✅ CONFIRMATION PRODUCTION")
print("=" * 50)

# Configuration
print(f"SECRET_KEY: {settings.SECRET_KEY[:20]}...")
print(f"STRIPE_SECRET_KEY: {settings.STRIPE_SECRET_KEY[:20]}...")
print(f"STRIPE_PUBLISHABLE_KEY: {settings.STRIPE_PUBLISHABLE_KEY[:20]}...")
print(f"EMAIL: {settings.EMAIL_HOST_USER}")
print(f"DEBUG: {settings.DEBUG}")

# Vérification complète
tests = [
    ("SECRET_KEY Django", len(settings.SECRET_KEY) > 20),
    ("Stripe Production", settings.STRIPE_SECRET_KEY.startswith('sk_live_')),
    ("Email Configuré", bool(settings.EMAIL_HOST_PASSWORD)),
    ("DEBUG désactivé", not settings.DEBUG),
]

print("\n🔍 Résultats des tests:")
all_passed = True
for test_name, passed in tests:
    status = "✅" if passed else "❌"
    print(f"  {status} {test_name}")
    if not passed:
        all_passed = False

# Test API Stripe
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    balance = stripe.Balance.retrieve()
    print("✅ Stripe API: Connexion réussie")
except Exception as e:
    print(f"❌ Stripe API: {e}")
    all_passed = False

print("=" * 50)

if all_passed:
    print("🎉 TOUT EST CORRECT !")
    print("🚀 VOTRE APPLICATION EST MAINTENANT EN PRODUCTION")
else:
    print("⚠️  Certains problèmes doivent être résolus")