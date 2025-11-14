from django.core.management.base import BaseCommand
from django.db import transaction
from swigo.models import PouletOption, Plat, Categorie


class Command(BaseCommand):
    help = 'Crée les options poulet pour la carte En Route Chef'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime toutes les options poulet existantes avant de créer les nouvelles',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        
        with transaction.atomic():
            if reset:
                self.stdout.write("🗑️  Suppression des options poulet existantes...")
                PouletOption.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS("✅ Options poulet existantes supprimées")
                )

            self.create_poulet_options()
            self.update_existing_poulet_plats()

    def create_poulet_options(self):
        """Crée toutes les options poulet avec la nouvelle structure à 4 accordéons"""
        options_data = [
            # 🎯 ASSAISONNEMENTS (PREMIER ACCORDÉON)
            {"nom": "Mild (doux)", "categorie": "assaisonnement", "prix_supplement": 0.00, "ordre": 1},
            {"nom": "Hot (épicé)", "categorie": "assaisonnement", "prix_supplement": 0.00, "ordre": 2},

            # 🍟 ACCOMPAGNEMENTS (DEUXIÈME ACCORDÉON)
            {"nom": "Frites maison", "categorie": "accompagnement", "prix_supplement": 0.00, "ordre": 1},
            {"nom": "Riz basmati", "categorie": "accompagnement", "prix_supplement": 0.00, "ordre": 2},
            {"nom": "Semoule", "categorie": "accompagnement", "prix_supplement": 0.00, "ordre": 3},
            {"nom": "Salade verte", "categorie": "accompagnement", "prix_supplement": 0.00, "ordre": 4},
            {"nom": "Kemia (Carotte+Olives épicés)", "categorie": "accompagnement", "prix_supplement": 0.00, "ordre": 5},
            {"nom": "Coleslaw maison", "categorie": "accompagnement", "prix_supplement": 0.30, "ordre": 6},
            {"nom": "Onion rings maison (6 pcs)", "categorie": "accompagnement", "prix_supplement": 0.50, "ordre": 7},
            {"nom": "Galette rösti maison", "categorie": "accompagnement", "prix_supplement": 0.70, "ordre": 8},
            {"nom": "Mozzarella sticks maison (3 pcs)", "categorie": "accompagnement", "prix_supplement": 0.90, "ordre": 9},
            {"nom": "Pain Maison", "categorie": "accompagnement", "prix_supplement": 2.00, "ordre": 10},

            # 🍯 SAUCES AU CHOIX (TROISIÈME ACCORDÉON)
            {"nom": "Mayonnaise maison", "categorie": "sauce", "prix_supplement": 0.00, "ordre": 1},
            {"nom": "Ketchup maison", "categorie": "sauce", "prix_supplement": 0.00, "ordre": 2},
            {"nom": "Sauce Miel-Moutarde", "categorie": "sauce", "prix_supplement": 0.00, "ordre": 3},
            {"nom": "Sauce Mayo piment d'Espelette", "categorie": "sauce", "prix_supplement": 0.50, "ordre": 4},
            {"nom": "Sauce Relish", "categorie": "sauce", "prix_supplement": 0.50, "ordre": 5},
            {"nom": "Sauce Raifort & Sriracha fumée", "categorie": "sauce", "prix_supplement": 0.50, "ordre": 6},
            {"nom": "Sauce BBQ Myrtilles & Habanero", "categorie": "sauce", "prix_supplement": 0.50, "ordre": 7},
            {"nom": "Auntie Sauce", "categorie": "sauce", "prix_supplement": 0.50, "ordre": 8},

            # ➕ SUPPLÉMENTS (QUATRIÈME ACCORDÉON)
            {"nom": "Portion supplémentaire de sauce", "categorie": "supplement", "prix_supplement": 0.50, "ordre": 1},
            {"nom": "Fromage supplémentaire", "categorie": "supplement", "prix_supplement": 1.00, "ordre": 2},
        ]

        created_count = 0
        for data in options_data:
            obj, created = PouletOption.objects.get_or_create(
                nom=data['nom'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ {data['nom']} - {data['categorie']}")
            else:
                # Mettre à jour la catégorie si elle a changé
                if obj.categorie != data['categorie']:
                    obj.categorie = data['categorie']
                    obj.save()
                    self.stdout.write(f"🔄 {data['nom']} - Catégorie mise à jour vers '{data['categorie']}'")
                else:
                    self.stdout.write(f"⚠️  {data['nom']} (existe déjà)")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 {created_count} options poulet créées/mises à jour sur {len(options_data)} au total"
            )
        )

    def update_existing_poulet_plats(self):
        """Met à jour les plats poulet existants pour leur assigner le type_plat='poulet'"""
        # Récupérer ou créer la catégorie Poulet
        categorie, created = Categorie.objects.get_or_create(
            nom="Poulet",
            defaults={'icone': 'fa-solid fa-drumstick-bite'}
        )
        
        if created:
            self.stdout.write(f"✅ Catégorie 'Poulet' créée")
        else:
            self.stdout.write(f"✅ Catégorie 'Poulet' déjà existante")

        # Liste des noms de plats poulet attendus
        noms_plats_poulet = [
            "5 Tenders croustillants",
            "5 Wings croustillants", 
            "5 Tenders + 5 Wings",
            "10 Tenders + 10 Wings",
            "1⁄4 poulet Josper",
            "1⁄2 poulet Josper",
            "Poulet entier Josper",
            "5 Wings Josper",
            "10 Wings Josper",
            "20 Wings Josper",
            "Bucket Mix Josper",
            "Bucket Mix Josper x2", 
            "Bucket Mix Josper x4",
        ]

        updated_count = 0
        for nom_plat in noms_plats_poulet:
            try:
                plat = Plat.objects.get(nom=nom_plat)
                # Mettre à jour le type_plat et la catégorie
                if plat.type_plat != 'poulet' or plat.categorie != categorie:
                    plat.type_plat = 'poulet'
                    plat.categorie = categorie
                    plat.save()
                    updated_count += 1
                    self.stdout.write(f"✅ {nom_plat} - Type mis à jour vers 'poulet'")
                else:
                    self.stdout.write(f"ℹ️  {nom_plat} - Déjà configuré")
            except Plat.DoesNotExist:
                self.stdout.write(f"❌ {nom_plat} - Plat non trouvé dans la base")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🍗 {updated_count} plats poulet mis à jour"
            )
        )

        # Résumé final
        total_plats_poulet = Plat.objects.filter(type_plat='poulet').count()
        total_options = PouletOption.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 IMPLÉMENTATION TERMINÉE !"
                f"\n📊 Récapitulatif :"
                f"\n   • {total_options} options poulet"
                f"\n   • {total_plats_poulet} plats configurés comme type 'poulet'"
                f"\n   • Assaisonnements: {PouletOption.objects.filter(categorie='assaisonnement').count()} options"
                f"\n   • Accompagnements: {PouletOption.objects.filter(categorie='accompagnement').count()} options"
                f"\n   • Sauces: {PouletOption.objects.filter(categorie='sauce').count()} options"
                f"\n   • Suppléments: {PouletOption.objects.filter(categorie='supplement').count()} options"
                f"\n\n🚀 Les 4 accordéons poulet sont maintenant disponibles !"
            )
        )