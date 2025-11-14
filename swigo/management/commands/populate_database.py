from django.core.management.base import BaseCommand
from decimal import Decimal, ROUND_HALF_UP
from swigo.models import (
    Categorie, Plat, Ingredient,
    ProduitTransforme, Option,
    Cuisson
)

class Command(BaseCommand):
    help = 'Populate the database with sample data for categories, ingredients, plats, options, and cuissons'

    def handle(self, *args, **kwargs):
        self.stdout.write("Démarrage de la population de la base de données...")
        self.create_categories()
        self.create_ingredients()
        self.stdout.write(self.style.SUCCESS("Population de la base de données terminée."))

    def create_categories(self):
        categories_data = [
            {'nom': 'Desserts', 'icone': 'flaticon-dessert'},
            {'nom': 'Boissons', 'icone': 'flaticon-boisson-non-alcoolisee'},
            {'nom': 'Pâtes', 'icone': 'flaticon-farfalle'},
            {'nom': 'Poulet', 'icone': 'flaticon-poulet-frit'},
            {'nom': 'Couscous', 'icone': 'flaticon-tajine-1'},
            {'nom': 'Salade', 'icone': 'flaticon-salade'},
            {'nom': 'Burger', 'icone': 'flaticon-burger'},
            {'nom': 'Menu', 'icone': 'flaticon-menu'}
        ]
        for data in categories_data:
            obj, created = Categorie.objects.get_or_create(**data)
            if created:
                self.stdout.write(f"Catégorie créée : {obj.nom}")
            else:
                self.stdout.write(f"Catégorie existante, non créée : {obj.nom}")

    def create_ingredients(self):
        ingredients_data = [
            # Ingrédients vendables directement
            {'nom': 'Jus d\'Orange', 'quantite_stock': 100, 'unite_stock': 'l', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'boissons', 'vendable_directement': True, 'taux_tva_achat': Decimal('5.5'), 'taux_tva_vente': Decimal('5.5'), 'prix_unitaire_vente': Decimal('3.00')},
            {'nom': 'Soda', 'quantite_stock': 100, 'unite_stock': 'l', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'boissons', 'vendable_directement': True, 'taux_tva_achat': Decimal('5.5'), 'taux_tva_vente': Decimal('5.5'), 'prix_unitaire_vente': Decimal('2.50')},
            # Autres ingrédients (non vendables directement)
            {'nom': 'Pain Burger', 'quantite_stock': 200, 'unite_stock': 'u', 'prix_unitaire_achat': Decimal('0.30'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Tomate', 'quantite_stock': 3000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Salade', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Poulet', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('8.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Pâtes', 'quantite_stock': 10000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.00'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Sucre', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('0.80'), 'groupe': 'sucres', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Oeuf', 'quantite_stock': 500, 'unite_stock': 'u', 'prix_unitaire_achat': Decimal('0.20'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Lait', 'quantite_stock': 1000, 'unite_stock': 'l', 'prix_unitaire_achat': Decimal('1.00'), 'groupe': 'laitiers', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Fromage', 'quantite_stock': 1500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('4.00'), 'groupe': 'laitiers', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Semoule Fine', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.20'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Pois Chiche', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Raisin', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('4.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Harissa', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('5.00'), 'groupe': 'epices', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Navet', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Carottes', 'quantite_stock': 3000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Courgettes', 'quantite_stock': 2500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.80'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Merguez', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('10.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Thon', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('8.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Crème Fraîche', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'laitiers', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Corn Flakes', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.50'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Farine', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('0.50'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Sauce Barbecue', 'quantite_stock': 1000, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('0.10'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce Piquante', 'quantite_stock': 1000, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('0.10'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            
            # Bases
            {'nom': 'Salade de saison', 'quantite_stock': 10000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Pâtes fraîches maison', 'quantite_stock': 8000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Mix Salade de saison / Pâtes fraîches maison', 'quantite_stock': 6000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.50'), 'groupe': 'melanges', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Quinoa', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Mix Quinoa / Salade de saison', 'quantite_stock': 4000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.50'), 'groupe': 'melanges', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Semoule', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.20'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Mix Semoule / Salade de saison', 'quantite_stock': 3000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'melanges', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Riz vinaigré', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.50'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Mix Riz vinaigré / Salade de saison', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.80'), 'groupe': 'melanges', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},

            # Protéines
            {'nom': 'Pavé de Saumon', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('15.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Pavé de Thon', 'quantite_stock': 1500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('12.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Filet de poisson pané', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('10.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Poulet Braisé', 'quantite_stock': 3000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('10.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Poulet Pané', 'quantite_stock': 2500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('11.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Agneau confit', 'quantite_stock': 1500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('18.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Agneau grillé', 'quantite_stock': 1500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('18.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Merguez', 'quantite_stock': 5000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('10.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Brochette de viande hachée charolaise', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('12.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Boulette de viande charolaise', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('12.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('10.0')},
            {'nom': 'Œuf', 'quantite_stock': 500, 'unite_stock': 'u', 'prix_unitaire_achat': Decimal('0.20'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Steak végétal', 'quantite_stock': 1500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('8.00'), 'groupe': 'vpo', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},

            # Garnitures
            {'nom': 'Courgettes râpées', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Champignons de Paris', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Chou rouge', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Edamame', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('5.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Maïs', 'quantite_stock': 3000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.20'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Oignons rouges', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Poivrons', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Carottes râpées', 'quantite_stock': 3000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Chou blanc', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.80'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Concombre', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Olives noires', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('4.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Olives vertes', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('4.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Radis', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Tomates cerises', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Tomates séchées', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('8.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Aubergines marinées', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('5.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Avocat', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('10.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Pois chiches', 'quantite_stock': 2000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Ananas', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('5.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Mangue', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('6.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Pruneaux', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('8.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Raisins secs', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('5.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Abricots secs', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('6.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Galette de Pomme de Terre Rosti Maison', 'quantite_stock': 1000, 'unite_stock': 'u', 'prix_unitaire_achat': Decimal('2.50'), 'groupe': 'feculents', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Cornichon croquant', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('4.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Ratatouille provençale', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Câpres', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('10.00'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Onion rings', 'quantite_stock': 500, 'unite_stock': 'u', 'prix_unitaire_achat': Decimal('0.50'), 'groupe': 'legumes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},

            # Toppings
            {'nom': 'Oignons frits', 'quantite_stock': 1000, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('2.50'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Menthe fraîche', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('4.00'), 'groupe': 'herbes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Coriandre fraîche', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'herbes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Ciboulette fraîche', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'herbes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Basilic frais', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.50'), 'groupe': 'herbes', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Amandes grillées', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('15.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Cacahuètes grillées', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('5.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Mélange de graines (chia-courge-lin-sésame)', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('6.00'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},
            {'nom': 'Pignons de pin', 'quantite_stock': 300, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('20.00'), 'groupe': 'fruits', 'vendable_directement': False, 'taux_tva_achat': Decimal('5.5')},

            # Sauces
            {'nom': 'Sauce miel-moutarde', 'quantite_stock': 1000, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce crème fraîche et aneth', 'quantite_stock': 1000, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('1.50'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce vinaigrette iba', 'quantite_stock': 1000, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('1.20'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce pesto', 'quantite_stock': 500, 'unite_stock': 'g', 'prix_unitaire_achat': Decimal('3.00'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce soja salé et sésame', 'quantite_stock': 500, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('0.80'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce soja sucré', 'quantite_stock': 500, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('0.80'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce tartare', 'quantite_stock': 500, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('1.00'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce barbecue', 'quantite_stock': 800, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('1.20'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': 'Sauce sweet chili', 'quantite_stock': 500, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('0.90'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
            {'nom': "Huile d'olive extra et balsamique", 'quantite_stock': 1000, 'unite_stock': 'ml', 'prix_unitaire_achat': Decimal('2.00'), 'groupe': 'epicerie', 'vendable_directement': False, 'taux_tva_achat': Decimal('20.0')},
        ]

        for data in ingredients_data:
            obj, created = Ingredient.objects.get_or_create(nom=data['nom'], defaults=data)
            if created:
                self.stdout.write(f"Ingrédient créé : {obj.nom}")
            else:
                self.stdout.write(f"Ingrédient existant, non créé : {obj.nom}")



    def create_plats_for_all_categories(self, produits_transformes):
        description_longue = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum vestibulum. Cras venenatis euismod malesuada."

        plats_data = {
            'Desserts': [
                {'nom': 'Tiramisu', 'description_courte': 'Dessert italien au café', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('5.50'), 'taux_tva': Decimal('10.0')},
            ],
            'Boissons': [
                {'nom': 'Jus d\'Orange', 'description_courte': 'Boisson fruitée', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('2.75'), 'taux_tva': Decimal('5.5')},
            ],
            'Pâtes': [
                {'nom': 'Spaghetti Carbonara', 'description_courte': 'Pâtes à la sauce carbonara', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('9.90'), 'taux_tva': Decimal('10.0')},
                {'nom': 'Pâtes au Thon', 'description_courte': 'Pâtes avec thon et crème fraîche', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('10.45'), 'taux_tva': Decimal('10.0')},
            ],
            'Poulet': [
                {'nom': 'Poulet Grillé', 'description_courte': 'Poulet mariné grillé', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('13.20'), 'taux_tva': Decimal('10.0')},
                {'nom': 'Bucket Poulet', 'description_courte': 'Morceaux de poulet frits', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('15.40'), 'taux_tva': Decimal('10.0')},
            ],
            'Couscous': [
                {'nom': 'Couscous Royal', 'description_courte': 'Couscous avec plusieurs viandes', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('16.50'), 'taux_tva': Decimal('10.0')},
                {'nom': 'Couscous Merguez', 'description_courte': 'Couscous avec merguez', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('14.30'), 'taux_tva': Decimal('10.0')},
            ],
            'Salade': [
                {'nom': 'Salade Méditerranéenne', 'description_courte': 'Salade avec légumes frais', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('6.60'), 'taux_tva': Decimal('10.0')},
            ],
            'Burger': [
                {'nom': 'Burger Classique', 'description_courte': 'Burger au boeuf et fromage', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('8.80'), 'taux_tva': Decimal('10.0')},
                {'nom': 'Burger Double', 'description_courte': 'Burger double boeuf', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('13.20'), 'taux_tva': Decimal('10.0')},
            ],
            'Menu': [
                {'nom': 'Menu Enfant', 'description_courte': 'Plat, dessert et boisson pour enfant', 'description_longue': description_longue, 'prix_unitaire_ttc': Decimal('11.00'), 'taux_tva': Decimal('10.0')},
            ]
        }

        for category_name, plats_info in plats_data.items():
            category, created = Categorie.objects.get_or_create(nom=category_name)
            if created:
                self.stdout.write(f"Catégorie créée (depuis plats) : {category.nom}")
            else:
                self.stdout.write(f"Catégorie {category.nom} déjà existante (depuis plats).")

            for plat_info in plats_info:
                prix_unitaire_ttc = plat_info.pop('prix_unitaire_ttc')
                taux_tva = plat_info.pop('taux_tva')
                plat, created = Plat.objects.get_or_create(
                    categorie=category,
                    nom=plat_info['nom'],
                    defaults={
                        'description_courte': plat_info['description_courte'],
                        'description_longue': plat_info['description_longue'],
                        'prix_unitaire_ttc': prix_unitaire_ttc,
                        'taux_tva': taux_tva
                    }
                )
                if created:
                    self.stdout.write(f"Plat créé : {plat.nom}")
                else:
                    self.stdout.write(f"Plat existant, non créé : {plat.nom}")

                self.assign_ingredients_to_plat(plat, produits_transformes)
                self.create_options_for_plat(plat)
                self.assign_cuissons(plat)

   



    def assign_cuissons(self, plat):
        def create_cuisson(plat, ingredient=None, produit_transforme=None, quantite=0, mode_cuisson=''):
            obj, created = Cuisson.objects.get_or_create(
                plat=plat,
                ingredient=ingredient,
                produit_transforme=produit_transforme,
                quantite=quantite,
                mode_cuisson=mode_cuisson
            )
            if created:
                self.stdout.write(f"Cuisson créée : {plat.nom}, Mode : {mode_cuisson}, {ingredient or produit_transforme}")
            else:
                self.stdout.write(f"Cuisson existante : {plat.nom}, Mode : {mode_cuisson}, {ingredient or produit_transforme}")

        if plat.nom in ['Spaghetti Carbonara', 'Pâtes au Thon']:
            pates = Ingredient.objects.get(nom='Pâtes')
            create_cuisson(plat, ingredient=pates, quantite=200, mode_cuisson='cuiseur')
        elif plat.nom in ['Burger Classique', 'Burger Double']:
            steak_hache = ProduitTransforme.objects.get(nom='Steak Haché')
            quantite_steak = 150 if plat.nom == 'Burger Classique' else 300
            create_cuisson(plat, produit_transforme=steak_hache, quantite=quantite_steak, mode_cuisson='grill')
        elif plat.nom == 'Bucket Poulet':
            poulet = Ingredient.objects.get(nom='Poulet')
            create_cuisson(plat, ingredient=poulet, quantite=300, mode_cuisson='friteuse')
        elif plat.nom == 'Couscous Merguez':
            merguez = Ingredient.objects.get(nom='Merguez')
            create_cuisson(plat, ingredient=merguez, quantite=150, mode_cuisson='josper')
            semoule = Ingredient.objects.get(nom='Semoule Fine')
            create_cuisson(plat, ingredient=semoule, quantite=200, mode_cuisson='cuiseur')
        elif plat.nom == 'Couscous Royal':
            viande_hachee = ProduitTransforme.objects.get(nom='Viande Hachée')
            create_cuisson(plat, produit_transforme=viande_hachee, quantite=100, mode_cuisson='josper')
            poulet = Ingredient.objects.get(nom='Poulet')
            create_cuisson(plat, ingredient=poulet, quantite=150, mode_cuisson='grill')
            semoule = Ingredient.objects.get(nom='Semoule Fine')
            create_cuisson(plat, ingredient=semoule, quantite=200, mode_cuisson='cuiseur')
