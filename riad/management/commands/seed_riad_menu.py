from decimal import Decimal

from django.core.management.base import BaseCommand

from riad.models import (
    ProductCategory,
    Product,
    Menu,
    MenuSection,
    MenuSectionItem,
)


CATEGORIES = [
    ("Formule", 0),
    ("Mocktail", 1),
    ("Boisson", 2),
    ("Jus", 3),
    ("Eau", 4),
    ("Entrée", 5),
    ("Plat", 6),
    ("Dessert", 7),
    ("Coupe glacée", 8),
    ("Thé / Café", 9),
]


CATALOGUE = {
    "Mocktail": [
        "Citronnade marocaine maison",
        "Mojito sans alcool",
        "Sunset Marrakech",
    ],
    "Boisson": [
        "Coca-Cola 33 cl",
        "Coca-Cola Zéro 33 cl",
        "Ice Tea Pêche 33 cl",
        "Limonade 33 cl",
        "Orangina 25 cl",
    ],
    "Jus": [
        "Jus d'orange 25 cl",
        "Jus d'ananas 25 cl",
        "Jus de pomme 25 cl",
    ],
    "Eau": [
        "Eau minérale/gazeuse 1 L",
        "Eau minérale/gazeuse 1/2 L",
    ],
    "Entrée": [
        "Brick kefta, fromage & œuf coulant",
        "Brick thon, pomme de terre & œuf coulant",
        "Pastilla poulet & amandes",
        "Assortiment de salades marocaines & pain maison",
    ],
    "Plat": [
        "Couscous Royal",
        "Couscous végétarien",
        "Tajine végétarien",
        "Tajine poulet, olives & citron confit, pommes frites",
        "Tajine d'agneau aux pruneaux, amandes & abricots",
        "Tajine kefta aux œufs et pomme de terre",
        "Assiette de grillades marocaines & frites maison",
        "Couscous boulette & merguez",
        "Smash burger maison & frites maison",
        "Crousty tenders",
        "Mini couscous poulet",
        "Mini couscous boulette",
        "Mini burger & frites maison",
        "Mini crousty tenders",
    ],
    "Dessert": [
        "Assortiment de 3 pâtisseries marocaines",
        "Cœur fondant chocolat maison & glace vanille",
        "Salade d'oranges à la cannelle & fleur d'oranger",
        "Baghrir (crêpe mille trous), Amlou & miel",
        "Cookie maison",
        "Glace chocolat vanille",
        "Coupe de glace au choix",
    ],
    "Coupe glacée": [
        "Café Liégeois",
        "Chocolat Liégeois",
        "Caramel Liégeois",
        "Fruits Rouges",
        "Évasion Exotique",
        "Les 2 Palmiers",
    ],
    "Thé / Café": [
        "Thé à la menthe",
        "Café",
    ],
}


SHORT_NAMES = {
    "Brick kefta, fromage & œuf coulant": "Brick kefta",
    "Brick thon, pomme de terre & œuf coulant": "Brick thon",
    "Assortiment de salades marocaines & pain maison": "Salades marocaines",
    "Couscous végétarien": "Couscous végé",
    "Tajine végétarien": "Tajine végé",
    "Tajine poulet, olives & citron confit, pommes frites": "Tajine poulet",
    "Tajine d'agneau aux pruneaux, amandes & abricots": "Tajine agneau",
    "Tajine kefta aux œufs et pomme de terre": "Tajine kefta",
    "Assiette de grillades marocaines & frites maison": "Grillades marocaines",
    "Assortiment de 3 pâtisseries marocaines": "3 pâtisseries",
    "Cœur fondant chocolat maison & glace vanille": "Fondant chocolat",
    "Salade d'oranges à la cannelle & fleur d'oranger": "Salade d'oranges",
    "Baghrir (crêpe mille trous), Amlou & miel": "Baghrir Amlou & miel",
    "Smash burger maison & frites maison": "Smash burger",
    "Couscous boulette & merguez": "Couscous boulette-merguez",
    "Citronnade marocaine maison": "Citronnade maison",
}


PRODUCT_PRICES = {
    "Coca-Cola 33 cl": "3.50",
    "Coca-Cola Zéro 33 cl": "3.50",
    "Ice Tea Pêche 33 cl": "3.50",
    "Limonade 33 cl": "3.50",
    "Orangina 25 cl": "3.50",
    "Jus d'orange 25 cl": "3.50",
    "Jus d'ananas 25 cl": "3.50",
    "Jus de pomme 25 cl": "3.50",
    "Eau minérale/gazeuse 1/2 L": "3.50",
    "Eau minérale/gazeuse 1 L": "5.00",
    "Citronnade marocaine maison": "7.00",
    "Mojito sans alcool": "7.00",
    "Sunset Marrakech": "7.00",
    "Assortiment de 3 pâtisseries marocaines": "7.50",
    "Cœur fondant chocolat maison & glace vanille": "6.50",
    "Salade d'oranges à la cannelle & fleur d'oranger": "5.50",
    "Baghrir (crêpe mille trous), Amlou & miel": "5.50",
    "Cookie maison": "4.50",
    "Glace chocolat vanille": "5.00",
    "Café Liégeois": "7.00",
    "Chocolat Liégeois": "7.00",
    "Caramel Liégeois": "7.00",
    "Fruits Rouges": "7.00",
    "Évasion Exotique": "7.00",
    "Les 2 Palmiers": "7.00",
    "Thé à la menthe": "3.50",
    "Café": "2.50",
}


MENUS = [
    {
        "name": "Menu Découverte",
        "price": 35,
        "order": 1,
        "sections": [
            ("Formule", ["Entrée + Plat", "Plat + Dessert"]),
            ("Entrée", [
                "Brick kefta, fromage & œuf coulant",
                "Brick thon, pomme de terre & œuf coulant",
                "Assortiment de salades marocaines & pain maison",
            ]),
            ("Plat", [
                "Couscous Royal",
                "Couscous végétarien",
                "Tajine végétarien",
                "Tajine poulet, olives & citron confit, pommes frites",
                "Tajine kefta aux œufs et pomme de terre",
                "Assiette de grillades marocaines & frites maison",
            ]),
            ("Dessert", [
                "Assortiment de 3 pâtisseries marocaines",
                "Cœur fondant chocolat maison & glace vanille",
                "Salade d'oranges à la cannelle & fleur d'oranger",
                "Baghrir (crêpe mille trous), Amlou & miel",
            ]),
            ("Thé / Café", ["Thé à la menthe", "Café"]),
        ],
    },
    {
        "name": "Menu Signature",
        "price": 45,
        "order": 2,
        "sections": [
            ("Mocktail", [
                "Citronnade marocaine maison",
                "Mojito sans alcool",
                "Sunset Marrakech",
            ]),
            ("Entrée", [
                "Brick kefta, fromage & œuf coulant",
                "Brick thon, pomme de terre & œuf coulant",
                "Pastilla poulet & amandes",
                "Assortiment de salades marocaines & pain maison",
            ]),
            ("Plat", [
                "Couscous Royal",
                "Couscous végétarien",
                "Tajine végétarien",
                "Tajine poulet, olives & citron confit, pommes frites",
                "Tajine d'agneau aux pruneaux, amandes & abricots",
                "Tajine kefta aux œufs et pomme de terre",
                "Assiette de grillades marocaines & frites maison",
            ]),
            ("Dessert", [
                "Assortiment de 3 pâtisseries marocaines",
                "Cœur fondant chocolat maison & glace vanille",
                "Salade d'oranges à la cannelle & fleur d'oranger",
                "Coupe de glace au choix",
                "Baghrir (crêpe mille trous), Amlou & miel",
            ]),
            ("Thé / Café", ["Thé à la menthe", "Café"]),
        ],
    },
    {
        "name": "Menu Jeune",
        "price": 20,
        "order": 3,
        "sections": [
            ("Boisson", [
                "Coca-Cola 33 cl",
                "Coca-Cola Zéro 33 cl",
                "Ice Tea Pêche 33 cl",
                "Limonade 33 cl",
                "Orangina 25 cl",
            ]),
            ("Plat", [
                "Couscous boulette & merguez",
                "Smash burger maison & frites maison",
                "Crousty tenders",
            ]),
            ("Dessert", [
                "Cookie maison",
                "Glace chocolat vanille",
                "Baghrir (crêpe mille trous), Amlou & miel",
            ]),
        ],
    },
    {
        "name": "Menu Enfant",
        "price": 15,
        "order": 4,
        "sections": [
            ("Boisson", [
                "Jus d'orange 25 cl",
                "Jus d'ananas 25 cl",
                "Jus de pomme 25 cl",
            ]),
            ("Plat", [
                "Mini couscous poulet",
                "Mini couscous boulette",
                "Mini burger & frites maison",
                "Mini crousty tenders",
            ]),
            ("Dessert", [
                "Cookie maison",
                "Glace chocolat vanille",
                "Baghrir (crêpe mille trous), Amlou & miel",
            ]),
        ],
    },
]


SUB_CHOICE_PRODUCTS = {
    "Coupe de glace au choix": "Coupe glacée",
}

VAT_RATE_REDUCED = Decimal("5.50")
VAT_RATE_STANDARD = Decimal("10.00")
VAT_REDUCED_CATEGORIES = {"Eau", "Boisson", "Jus"}


class Command(BaseCommand):
    help = "Initialise le catalogue et les menus du Riad"

    def handle(self, *args, **kwargs):
        categories = {}

        for name, order in CATEGORIES:
            category, _ = ProductCategory.objects.update_or_create(
                name=name,
                defaults={"order": order, "is_active": True},
            )
            categories[name] = category

        for category_name, products in CATALOGUE.items():
            category = categories[category_name]
            vat_rate = (
                VAT_RATE_REDUCED
                if category_name in VAT_REDUCED_CATEGORIES
                else VAT_RATE_STANDARD
            )

            for product_name in products:
                Product.objects.update_or_create(
                    category=category,
                    name=product_name,
                    defaults={
                        "price": PRODUCT_PRICES.get(product_name, 0),
                        "is_active": True,
                        "short_name": SHORT_NAMES.get(product_name, ""),
                        "vat_rate": vat_rate,
                    },
                )

        for product_name, price in PRODUCT_PRICES.items():
            Product.objects.filter(name=product_name).update(price=price)

        formule_category = categories["Formule"]

        for formula_name in ["Entrée + Plat", "Plat + Dessert"]:
            Product.objects.update_or_create(
                category=formule_category,
                name=formula_name,
                defaults={
                    "price": 0,
                    "is_active": True,
                    "vat_rate": VAT_RATE_STANDARD,
                },
            )

        for product_name, sub_category_name in SUB_CHOICE_PRODUCTS.items():
            product = Product.objects.get(name=product_name)
            product.sub_choice_category = categories[sub_category_name]
            product.save(update_fields=["sub_choice_category"])

        for menu_data in MENUS:
            menu, _ = Menu.objects.update_or_create(
                name=menu_data["name"],
                defaults={
                    "price": menu_data["price"],
                    "order": menu_data["order"],
                    "is_active": True,
                },
            )

            for section_order, (section_name, product_names) in enumerate(
                menu_data["sections"],
                start=1,
            ):
                section, _ = MenuSection.objects.update_or_create(
                    menu=menu,
                    name=section_name,
                    defaults={
                        "order": section_order,
                        "required": True,
                    },
                )

                section.items.all().delete()

                for item_order, product_name in enumerate(product_names, start=1):
                    product = Product.objects.get(name=product_name)

                    MenuSectionItem.objects.create(
                        section=section,
                        product=product,
                        order=item_order,
                    )

        self.stdout.write(
            self.style.SUCCESS("Catalogue et menus du Riad créés avec succès.")
        )
