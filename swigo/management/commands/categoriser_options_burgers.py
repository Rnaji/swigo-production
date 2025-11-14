# swigo/management/commands/categoriser_toutes_options.py
from django.core.management.base import BaseCommand
from swigo.models import Option

class Command(BaseCommand):
    help = 'Catégorise TOUTES les options existantes'
    
    def handle(self, *args, **options):
        toutes_les_options = Option.objects.all()
        self.stdout.write(f"Options totales à traiter: {toutes_les_options.count()}")
        
        # Mapping COMPLET des catégories
        categorisation = {
            'supp_viande': [
                'extra smash 75g',
                'extra 150g', 
                'smash 75g',
                '150g',
                'extra',
                'smash',
            ],
            'supp_fromage': [
                'cheddar',
                'comté', 
                'raclette',
                'reblochon',
                'chèvre',
            ],
            'supp_croustillant': [
                'rösti',
                'onion rings',
                'onion',
            ],
            'supp_sauce': [
                'sauce mayonnaise',
                'sauce ketchup',
                'sauce miel-moutarde',
                'sauce mayo piment',
                'sauce relish',
                'sauce raifort',
                'sauce sriracha',
                'sauce bbq',
                'auntie sauce',
                'mayonnaise',
                'ketchup',
                'miel-moutarde',
                'relish',
                'raifort',
                'bbq',
                'auntie',
            ]
        }
        
        # Ordre spécifique pour chaque catégorie
        ordre_par_categorie = {
            'supp_viande': {
                'extra smash 75g': 1,
                'extra 150g': 2,
                'smash 75g': 1,
                '150g': 2,
            },
            'supp_fromage': {
                'cheddar': 1,
                'comté': 2,
                'raclette': 3,
                'reblochon': 4,
                'chèvre': 5,
            },
            'supp_croustillant': {
                'rösti': 1,
                'onion rings': 2,
            },
            'supp_sauce': {
                'sauce mayonnaise': 1,
                'sauce ketchup': 2,
                'sauce miel-moutarde': 3,
                'sauce mayo piment': 4,
                'sauce relish': 5,
                'sauce raifort': 6,
                'sauce sriracha': 7,
                'sauce bbq': 8,
                'auntie sauce': 9,
            }
        }
        
        options_categorisees = 0
        
        for option in toutes_les_options:
            nom_lower = option.nom_option.lower()
            ancienne_categorie = option.categorie
            option_categorisee = False
            
            # Chercher dans chaque catégorie
            for categorie, mots_cles in categorisation.items():
                for mot_cle in mots_cles:
                    if mot_cle in nom_lower:
                        option.categorie = categorie
                        
                        # Déterminer l'ordre
                        ordre_trouve = False
                        for pattern_ordre, ordre_value in ordre_par_categorie.get(categorie, {}).items():
                            if pattern_ordre in nom_lower:
                                option.ordre = ordre_value
                                ordre_trouve = True
                                break
                        
                        if not ordre_trouve:
                            option.ordre = 99  # Ordre par défaut
                        
                        option.save()
                        options_categorisees += 1
                        option_categorisee = True
                        
                        changement = f"({ancienne_categorie} → {categorie})" if ancienne_categorie != categorie else ""
                        self.stdout.write(f"✅ {option.nom_option} → {categorie} ordre:{option.ordre} {changement}")
                        break
                
                if option_categorisee:
                    break
            
            if not option_categorisee:
                self.stdout.write(f"❓ {option.nom_option} → NON CATÉGORISÉE")
        
        # Résumé final
        self.stdout.write(f"\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("CATÉGORISATION TERMINÉE !"))
        self.stdout.write(f"Options traitées: {toutes_les_options.count()}")
        self.stdout.write(f"Options catégorisées: {options_categorisees}")
        
        # Statistiques détaillées
        self.stdout.write(f"\n📊 RÉPARTITION PAR CATÉGORIE:")
        for categorie_code, categorie_nom in Option.CATEGORIE_OPTION_CHOICES:
            count = Option.objects.filter(categorie=categorie_code).count()
            pourcentage = (count / toutes_les_options.count()) * 100
            self.stdout.write(f"  {categorie_nom}: {count} options ({pourcentage:.1f}%)")
        
        # Aperçu des options par catégorie
        self.stdout.write(f"\n👀 APERÇU PAR CATÉGORIE:")
        for categorie_code, categorie_nom in Option.CATEGORIE_OPTION_CHOICES:
            options_cat = Option.objects.filter(categorie=categorie_code)[:3]  # 3 premières
            if options_cat:
                self.stdout.write(f"\n  {categorie_nom}:")
                for opt in options_cat:
                    self.stdout.write(f"    - {opt.nom_option} (ordre: {opt.ordre})")