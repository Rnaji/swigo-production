# management/commands/creer_limites_poulet.py

from django.core.management.base import BaseCommand
from django.db import transaction
from swigo.models import Plat, LimiteOptionsPoulet

class Command(BaseCommand):
    help = 'Crée les limites d\'options pour les plats poulet'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans modifier la base',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        configurations_limites = {
            'Bucket Mix Josper 4 pers': [1, 4, 4, 99],
            'Mix Josper 2 pers': [1, 2, 2, 99],
            'Mix Josper 1 pers': [1, 1, 1, 99],
            'Wings Josper 20 pcs': [1, 4, 4, 99],
            'Wings Josper 10 pcs': [1, 2, 2, 99],
            'Wings Josper 5 pcs': [1, 1, 1, 99],
            'Poulet entier Josper (~1,4kg)': [1, 4, 4, 99],
            '1⁄2 poulet Josper (~700g)': [1, 2, 2, 99],
            '1⁄4 poulet Josper (~350g)': [1, 1, 1, 99],
            '10 TENDERS FRITS + 10 WINGS FRITS': [1, 4, 4, 99],
            '5 TENDERS FRITS + 5 WINGS FRITS': [1, 2, 2, 99],
            '5 WINGS FRITS': [1, 1, 1, 99],
            '5 TENDERS FRITS': [1, 1, 1, 99],
        }
        
        categories = ['assaisonnement', 'accompagnement', 'sauce', 'supplement']
        
        if dry_run:
            self.stdout.write("🚧 MODE DRY RUN - Aucune modification ne sera faite")
        
        with transaction.atomic():
            if dry_run:
                # Désactive réellement les modifications en dry-run
                transaction.set_rollback(True)
            
            for nom_plat, limites in configurations_limites.items():
                try:
                    plat = Plat.objects.get(nom=nom_plat, type_plat='poulet')
                    
                    if dry_run:
                        self.stdout.write(f"🔧 [DRY RUN] Configuration de {nom_plat}")
                    else:
                        self.stdout.write(f"🔧 Configuration de {nom_plat}")
                    
                    for i, categorie in enumerate(categories):
                        if not dry_run:
                            LimiteOptionsPoulet.objects.update_or_create(
                                plat=plat,
                                categorie=categorie,
                                defaults={'limite_selection': limites[i]}
                            )
                        
                        self.stdout.write(
                            f"   ✅ {categorie}: {limites[i]} choix "
                            f"{'(illimité)' if limites[i] == 99 else ''}"
                        )
                        
                except Plat.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"❌ Plat non trouvé: {nom_plat}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erreur avec {nom_plat}: {e}"))
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Configuration terminée avec succès !")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"\n🔍 Dry-run terminé - Aucune modification effectuée")
            )