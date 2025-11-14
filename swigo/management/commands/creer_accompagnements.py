# swigo/management/commands/creer_accompagnements.py
from django.core.management.base import BaseCommand
from swigo.models import Accompagnement
from decimal import Decimal

class Command(BaseCommand):
    help = 'Créer les accompagnements pour les burgers'
    
    def handle(self, *args, **options):
        accompagnements_data = [
            {'nom': 'Frites Classiques', 'prix_supplement': Decimal('0.00'), 'ordre': 1, 'disponible': True},
            {'nom': 'Riz Basmati', 'prix_supplement': Decimal('0.00'), 'ordre': 2, 'disponible': True},
            {'nom': 'Semoule', 'prix_supplement': Decimal('0.00'), 'ordre': 3, 'disponible': True},
            {'nom': 'Salade Verte', 'prix_supplement': Decimal('0.00'), 'ordre': 4, 'disponible': True},
            {'nom': 'Kemia', 'prix_supplement': Decimal('0.00'), 'ordre': 5, 'disponible': True},
            {'nom': 'Coleslaw', 'prix_supplement': Decimal('0.30'), 'ordre': 6, 'disponible': True},
            {'nom': 'Onion Rings', 'prix_supplement': Decimal('0.50'), 'ordre': 7, 'disponible': True},
            {'nom': 'Galette Rösti', 'prix_supplement': Decimal('0.70'), 'ordre': 8, 'disponible': True},
            {'nom': 'Mozzarella Sticks (2 pcs)', 'prix_supplement': Decimal('0.90'), 'ordre': 9, 'disponible': True},
        ]
        
        for data in accompagnements_data:
            acc, created = Accompagnement.objects.get_or_create(
                nom=data['nom'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Créé: {acc.nom} (ID: {acc.id})"))
            else:
                self.stdout.write(f"📋 Existe déjà: {acc.nom} (ID: {acc.id})")
        
        self.stdout.write(self.style.SUCCESS("🎉 Tous les accompagnements sont prêts!"))