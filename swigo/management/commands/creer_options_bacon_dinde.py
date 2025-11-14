# swigo/management/commands/creer_options_bacon_dinde.py
from django.core.management.base import BaseCommand
from swigo.models import Option, Plat, Ingredient
from decimal import Decimal

class Command(BaseCommand):
    help = 'Crée les options Extra bacon de dinde pour tous les burgers'
    
    def handle(self, *args, **options):
        # Trouver l'ingrédient Bacon de dinde
        try:
            bacon_dinde = Ingredient.objects.get(nom__icontains='bacon de dinde')
            self.stdout.write(f"✅ Ingredient trouvé: {bacon_dinde.nom}")
        except Ingredient.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Bacon de dinde non trouvé dans les ingrédients"))
            return
        except Ingredient.MultipleObjectsReturned:
            bacon_dinde = Ingredient.objects.filter(nom__icontains='bacon de dinde').first()
            self.stdout.write(f"✅ Plusieurs bacons trouvés, utilisation du premier: {bacon_dinde.nom}")
        
        # Trouver tous les burgers (plats qui ont des options)
        burgers = Plat.objects.filter(option__isnull=False).distinct()
        self.stdout.write(f"🔄 Burgers trouvés: {burgers.count()}")
        
        options_crees = 0
        
        for burger in burgers:
            # Vérifier si l'option existe déjà
            option_existante = Option.objects.filter(
                plat=burger, 
                nom_option__icontains='bacon'
            ).exists()
            
            if not option_existante:
                # Créer l'option Extra bacon de dinde
                nouvelle_option = Option(
                    plat=burger,
                    nom_option="Extra bacon de dinde",
                    prix_unitaire_ttc=Decimal('2.50'),  # Prix à ajuster selon votre tarif
                    taux_tva=10,  # TVA standard
                    categorie='supp_viande',
                    ordre=3  # Après Extra smash 75g (1) et Extra 150g (2)
                )
                nouvelle_option.save()
                options_crees += 1
                self.stdout.write(f"✅ Option créée pour: {burger.nom}")
            else:
                self.stdout.write(f"⏭️  Option bacon existe déjà pour: {burger.nom}")
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Création terminée: {options_crees} nouvelles options créées"))
        
        # Vérification finale
        total_options_bacon = Option.objects.filter(nom_option__icontains='bacon').count()
        self.stdout.write(f"📊 Total options bacon après création: {total_options_bacon}")