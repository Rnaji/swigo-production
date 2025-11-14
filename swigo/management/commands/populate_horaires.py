from django.core.management.base import BaseCommand
from datetime import time
from swigo.models import HoraireDisponible

class Command(BaseCommand):
    help = 'Remplit la base de données avec des horaires disponibles par défaut'

    def handle(self, *args, **kwargs):
        jours = ['LUN', 'MAR', 'MER', 'JEU', 'VEN', 'SAM', 'DIM']
        services = {
            'MIDI': (time(12, 0), time(14, 0)),  # 12h00 - 14h00
            'SOIR': (time(19, 0), time(22, 0))   # 19h00 - 22h00
        }
        intervalle = 15
        capacite_max = 10

        for jour in jours:
            for service, (heure_debut, heure_fin) in services.items():
                # Vérifier si l'horaire existe déjà pour éviter les doublons
                if not HoraireDisponible.objects.filter(jour=jour, service=service).exists():
                    HoraireDisponible.objects.create(
                        jour=jour,
                        service=service,
                        heure_debut=heure_debut,
                        heure_fin=heure_fin,
                        intervalle=intervalle,
                        capacite_max=capacite_max,
                        nombre_commandes=0
                    )
                    self.stdout.write(self.style.SUCCESS(f"Horaire ajouté pour {jour} - {service}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Horaire déjà existant pour {jour} - {service}"))

        self.stdout.write(self.style.SUCCESS('Tous les horaires ont été ajoutés avec succès !'))
