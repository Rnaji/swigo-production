# swigo/apps.py
from django.apps import AppConfig

class SwigoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'swigo'

    def ready(self):
        # Importer les signaux lors du démarrage de l'application
        import swigo.signals
