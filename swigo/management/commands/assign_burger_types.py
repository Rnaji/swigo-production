# management/commands/assign_burger_types.py
from django.core.management.base import BaseCommand
from swigo.models import Plat, Categorie

class Command(BaseCommand):
    help = 'Assigner les types de burgers aux plats existants'

    def handle(self, *args, **options):
        try:
            categorie_burger = Categorie.objects.get(nom__iexact='burger')
            
            # Burgers classiques
            classiques = [
                'Original ERC', 'Cheese Lover', 'Double Cheese Smash',
                'Triple Cheese Smash', 'Smoky Double', 'Crunchy Chicken', 'Veggie Classic'
            ]
            
            # Burgers gourmets
            gourmets = [
                'Hot Jalapeño', 'Campagnard', 'Rösti Comté',
                'Big Fromager', 'Josper Rings Signature', 'Veggie Gourmet', 'Poulet Josper'
            ]
            
            for nom in classiques:
                Plat.objects.filter(
                    categorie=categorie_burger,
                    nom__icontains=nom
                ).update(type_burger='classique')
            
            for nom in gourmets:
                Plat.objects.filter(
                    categorie=categorie_burger,
                    nom__icontains=nom
                ).update(type_burger='gourmet')
            
            self.stdout.write(
                self.style.SUCCESS('Types de burgers assignés avec succès!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur: {e}')
            )