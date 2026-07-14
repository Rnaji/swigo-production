from django.core.management.base import BaseCommand

from riad.models import (
    ProductCategory,
    Product,
    Menu,
    MenuSection,
    MenuSectionItem,
)


CATEGORIES = [
    ("Mocktail", 1),
    ("Boisson", 2),
    ("Entrée", 3),
    ("Plat", 4),
    ("Dessert", 5),
    ("Thé / Café", 6),
    ("Eau", 7),
    ("Supplément", 8),
]


CATALOGUE = {
    "Mocktail": [
        "Citronnade marocaine",
        "Mojito sans alcool",
    ],
    "Boisson": [
        "Coca-Cola",
        "Limonade",
        "Ice Tea",
    ],
    "Entrée": [
        "Brick kefta, fromage & œuf",
        "Brick thon, pomme de terre & œuf",
        "Pastilla poulet & amandes",
        "Assortiment de salades marocaines",
    ],
    "Plat": [
        "Couscous Royal",
        "Couscous végétarien",
        "Tajine végétarien",
        "Tajine poulet olives citron",
        "Tajine agneau pruneaux",
        "Assiette de grillades marocaines",
        "Smash burger maison",
        "Crousty tenders",
        "Couscous boulette & merguez",
        "Mini couscous",
        "Mini burger",
    ],
    "Dessert": [
        "3 pâtisseries marocaines",
        "Fondant chocolat",
        "Salade d'oranges",
        "Cookie maison",
        "Glace vanille",
    ],
    "Thé / Café": [
        "Thé à la menthe",
        "Café",
    ],
    "Eau": [
        "Eau plate",
        "Eau gazeuse",
    ],
    "Supplément": [
        "Merguez",
        "Brochette",
        "Portion de frites",
    ],
}


MENUS = [
    {
        "name": "Menu Découverte",
        "price": 35,
        "order": 1,
        "sections": [
            ("Formule", ["Entrée + Plat", "Plat + Dessert"]),
            ("Entrée", [
                "Brick kefta, fromage & œuf",
                "Brick thon, pomme de terre & œuf",
                "Assortiment de salades marocaines",
            ]),
            ("Plat", [
                "Couscous Royal",
                "Couscous végétarien",
                "Tajine végétarien",
                "Tajine poulet olives citron",
                "Assiette de grillades marocaines",
            ]),
            ("Dessert", [
                "3 pâtisseries marocaines",
                "Fondant chocolat",
                "Salade d'oranges",
            ]),
            ("Thé / Café", ["Thé à la menthe", "Café"]),
            ("Eau", ["Eau plate", "Eau gazeuse"]),
        ],
    },
    {
        "name": "Menu Signature",
        "price": 45,
        "order": 2,
        "sections": [
            ("Mocktail", ["Citronnade marocaine", "Mojito sans alcool"]),
            ("Entrée", [
                "Brick kefta, fromage & œuf",
                "Brick thon, pomme de terre & œuf",
                "Pastilla poulet & amandes",
                "Assortiment de salades marocaines",
            ]),
            ("Plat", [
                "Couscous Royal",
                "Couscous végétarien",
                "Tajine végétarien",
                "Tajine poulet olives citron",
                "Tajine agneau pruneaux",
                "Assiette de grillades marocaines",
            ]),
            ("Dessert", [
                "3 pâtisseries marocaines",
                "Fondant chocolat",
                "Salade d'oranges",
            ]),
            ("Thé / Café", ["Thé à la menthe", "Café"]),
            ("Eau", ["Eau plate", "Eau gazeuse"]),
        ],
    },
    {
        "name": "Menu Jeune",
        "price": 20,
        "order": 3,
        "sections": [
            ("Boisson", ["Coca-Cola", "Limonade", "Ice Tea"]),
            ("Plat", [
                "Smash burger maison",
                "Couscous boulette & merguez",
                "Crousty tenders",
            ]),
            ("Dessert", ["Cookie maison", "Glace vanille"]),
        ],
    },
    {
        "name": "Menu Enfant",
        "price": 15,
        "order": 4,
        "sections": [
            ("Boisson", ["Coca-Cola", "Limonade", "Ice Tea"]),
            ("Plat", ["Mini couscous", "Mini burger", "Crousty tenders"]),
            ("Dessert", ["Cookie maison", "Glace vanille"]),
        ],
    },
]


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

            for product_name in products:
                Product.objects.update_or_create(
                    category=category,
                    name=product_name,
                    defaults={"price": 0, "is_active": True},
                )

        formule_category, _ = ProductCategory.objects.update_or_create(
            name="Formule",
            defaults={"order": 0, "is_active": True},
        )

        for formula_name in ["Entrée + Plat", "Plat + Dessert"]:
            Product.objects.update_or_create(
                category=formule_category,
                name=formula_name,
                defaults={"price": 0, "is_active": True},
            )

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

                for item_order, product_name in enumerate(product_names, start=1):
                    product = Product.objects.get(name=product_name)

                    MenuSectionItem.objects.update_or_create(
                        section=section,
                        product=product,
                        defaults={"order": item_order},
                    )

        self.stdout.write(
            self.style.SUCCESS("Catalogue et menus du Riad créés avec succès.")
        )