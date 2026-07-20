from decimal import Decimal

from django.test import TestCase

from riad.models import (
    DiningOrder,
    DiningTable,
    GuestChoice,
    GuestOrder,
    Menu,
    MenuSection,
    MenuSectionItem,
    Product,
    ProductCategory,
    Room,
    TableService,
)
from riad.services.order_content import (
    compute_next_status,
    get_order_service_flags,
    order_has_desserts,
    order_has_starters,
    resolve_workflow_status,
    sync_service_flags_from_order,
)
from riad.services.workflow import get_workflow_step


class OrderContentTestMixin:
    def setUp(self):
        self.room = Room.objects.create(name="Salle test", order=1)
        self.table = DiningTable.objects.create(room=self.room, numero=99)
        self.service = TableService.objects.create(table=self.table, status="ordered")
        self.order = DiningOrder.objects.create(
            service=self.service,
            guests_count=2,
            is_sent_to_kitchen=True,
        )

        self.categories = {}
        for name in [
            "Entrée",
            "Plat",
            "Dessert",
            "Coupe glacée",
            "Thé / Café",
            "Mocktail",
            "Boisson",
        ]:
            self.categories[name] = ProductCategory.objects.create(name=name)

        self.products = {}
        for category_name, product_name in [
            ("Entrée", "Salade marocaine"),
            ("Plat", "Couscous Royal"),
            ("Dessert", "Pâtisseries marocaines"),
            ("Coupe glacée", "Les 2 Palmiers"),
            ("Thé / Café", "Thé à la menthe"),
            ("Mocktail", "Citronnade"),
            ("Boisson", "Coca-Cola"),
        ]:
            self.products[product_name] = Product.objects.create(
                category=self.categories[category_name],
                name=product_name,
                price=Decimal("5.00"),
            )

        self.menu = Menu.objects.create(name="Menu Découverte", price=Decimal("35.00"))

        self.sections = {}
        for order_idx, section_name in enumerate(
            ["Formule", "Entrée", "Plat", "Dessert", "Thé / Café"],
            start=1,
        ):
            section = MenuSection.objects.create(
                menu=self.menu,
                name=section_name,
                order=order_idx,
            )
            self.sections[section_name] = section

        for section_name, product_names in [
            ("Entrée", ["Salade marocaine"]),
            ("Plat", ["Couscous Royal"]),
            ("Dessert", ["Pâtisseries marocaines"]),
            ("Thé / Café", ["Thé à la menthe"]),
        ]:
            for product_name in product_names:
                MenuSectionItem.objects.create(
                    section=self.sections[section_name],
                    product=self.products[product_name],
                )

    def create_guest(self, guest_number, choices):
        guest = GuestOrder.objects.create(
            order=self.order,
            guest_number=guest_number,
            menu=self.menu,
        )

        for section_name, product_name, source in choices:
            GuestChoice.objects.create(
                guest=guest,
                section=self.sections[section_name],
                product=self.products[product_name],
                quantity=1,
                source=source,
            )

        return guest

    def create_table_extra(self, product_name, source="extra"):
        product = self.products[product_name]
        section = (
            MenuSection.objects.filter(items__product=product).first()
        )

        return GuestChoice.objects.create(
            order=self.order,
            guest=None,
            section=section,
            product=product,
            quantity=1,
            source=source,
            applied_vat_rate=product.vat_rate,
        )


class OrderContentFlagsTests(OrderContentTestMixin, TestCase):
    def test_two_menus_entree_plat_skip_dessert(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        self.create_guest(2, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])

        flags = get_order_service_flags(self.order)

        self.assertTrue(flags["has_starters"])
        self.assertTrue(flags["has_mains"])
        self.assertFalse(flags["has_desserts"])
        self.assertTrue(flags["has_coffee"])
        self.assertFalse(flags["has_drinks"])

        self.assertEqual(
            compute_next_status("mains_cleared", flags),
            "desserts_cleared",
        )

        self.service.status = "mains_cleared"
        workflow = get_workflow_step(
            resolve_workflow_status(self.service, self.order)
        )
        self.assertEqual(workflow["title"], "Servir les thés / cafés")

    def test_two_menus_plat_dessert_skip_starter(self):
        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
        ])
        self.create_guest(2, [
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
        ])

        flags = get_order_service_flags(self.order)

        self.assertFalse(flags["has_starters"])
        self.assertTrue(flags["has_mains"])
        self.assertTrue(flags["has_desserts"])

        self.assertEqual(
            compute_next_status("ordered", flags),
            "starters_cleared",
        )

    def test_menu_signature_full_service(self):
        mocktail_section = MenuSection.objects.create(
            menu=self.menu,
            name="Mocktail",
            order=0,
        )
        MenuSectionItem.objects.create(
            section=mocktail_section,
            product=self.products["Citronnade"],
        )

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        self.create_guest(2, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        self.create_table_extra("Citronnade")

        flags = get_order_service_flags(self.order)

        self.assertTrue(flags["has_drinks"])
        self.assertTrue(flags["has_starters"])
        self.assertTrue(flags["has_mains"])
        self.assertTrue(flags["has_desserts"])
        self.assertTrue(flags["has_coffee"])

        self.assertEqual(compute_next_status("ordered", flags), "drinks_served")
        self.assertEqual(compute_next_status("mains_cleared", flags), "desserts_served")

    def test_menu_jeune_only_relevant_steps(self):
        jeune_menu = Menu.objects.create(name="Menu Jeune", price=Decimal("20.00"))
        boisson_section = MenuSection.objects.create(menu=jeune_menu, name="Boisson", order=1)
        plat_section = MenuSection.objects.create(menu=jeune_menu, name="Plat", order=2)
        dessert_section = MenuSection.objects.create(menu=jeune_menu, name="Dessert", order=3)

        for section, product_name in [
            (boisson_section, "Coca-Cola"),
            (plat_section, "Couscous Royal"),
            (dessert_section, "Pâtisseries marocaines"),
        ]:
            MenuSectionItem.objects.create(
                section=section,
                product=self.products[product_name],
            )

        guest = GuestOrder.objects.create(
            order=self.order,
            guest_number=1,
            menu=jeune_menu,
        )
        GuestChoice.objects.create(
            guest=guest,
            section=boisson_section,
            product=self.products["Coca-Cola"],
            quantity=1,
            source="menu",
        )
        GuestChoice.objects.create(
            guest=guest,
            section=plat_section,
            product=self.products["Couscous Royal"],
            quantity=1,
            source="menu",
        )

        flags = get_order_service_flags(self.order)

        self.assertTrue(flags["has_drinks"])
        self.assertFalse(flags["has_starters"])
        self.assertTrue(flags["has_mains"])
        self.assertFalse(flags["has_desserts"])
        self.assertFalse(flags["has_coffee"])

        self.assertEqual(compute_next_status("ordered", flags), "drinks_served")
        self.assertEqual(compute_next_status("mains_cleared", flags), "bill_requested")

    def test_extra_dessert_after_order_enables_dessert_step(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])

        flags = get_order_service_flags(self.order)
        self.assertFalse(flags["has_desserts"])

        self.create_table_extra("Les 2 Palmiers")

        self.assertTrue(order_has_desserts(self.order))
        self.assertEqual(
            compute_next_status("mains_cleared", get_order_service_flags(self.order)),
            "desserts_served",
        )

    def test_coupe_sub_choice_counts_as_dessert(self):
        guest = self.create_guest(1, [
            ("Dessert", "Les 2 Palmiers", "menu"),
        ])

        choice = guest.choices.first()
        self.assertEqual(choice.section.name, "Dessert")
        self.assertEqual(choice.product.category.name, "Coupe glacée")
        self.assertTrue(order_has_desserts(self.order))

    def test_sync_service_flags_from_order(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])

        self.service.has_desserts = True
        self.service.has_coffee = True
        self.service.save()

        sync_service_flags_from_order(self.service, self.order)
        self.service.refresh_from_db()

        self.assertFalse(self.service.has_desserts)
        self.assertFalse(self.service.has_coffee)
        self.assertTrue(self.service.has_starters)

    def test_table_service_get_next_status_uses_live_order(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])

        self.service.status = "mains_cleared"
        self.service.has_desserts = True
        self.service.save()

        self.assertEqual(self.service.get_next_status(self.order), "desserts_cleared")


class PreTicketTests(OrderContentTestMixin, TestCase):
    def test_aggregate_menus_and_extras(self):
        menu_signature = Menu.objects.create(
            name="Menu Signature",
            price=Decimal("45.00"),
        )

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        self.create_guest(2, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])

        guest3 = GuestOrder.objects.create(
            order=self.order,
            guest_number=3,
            menu=menu_signature,
        )
        GuestChoice.objects.create(
            guest=guest3,
            section=self.sections["Entrée"],
            product=self.products["Salade marocaine"],
            quantity=1,
            source="menu",
        )

        boulettes = Product.objects.create(
            category=self.categories["Plat"],
            name="Boulettes",
            price=Decimal("2.00"),
        )
        caramel = Product.objects.create(
            category=self.categories["Dessert"],
            name="Caramel Liégeois",
            price=Decimal("7.00"),
        )

        GuestChoice.objects.create(
            guest=guest3,
            section=self.sections["Plat"],
            product=boulettes,
            quantity=2,
            source="extra",
            applied_vat_rate=boulettes.vat_rate,
        )

        GuestChoice.objects.create(
            order=self.order,
            guest=None,
            section=self.sections["Dessert"],
            product=caramel,
            quantity=1,
            source="extra",
            applied_vat_rate=caramel.vat_rate,
        )

        from riad.services.pre_ticket import build_pre_ticket

        ticket = build_pre_ticket(self.order)

        self.assertEqual(ticket["restaurant"]["name"], "LES 2 PALMIERS")
        self.assertEqual(ticket["disclaimer_line"], "NE TIENT PAS LIEU DE TICKET DE CAISSE")
        self.assertEqual(len(ticket["items"]), 2)
        self.assertEqual(ticket["items"][0]["display_label"], "2 × Menu Découverte")
        self.assertEqual(ticket["items"][0]["amount_display"], "70,00 €")
        self.assertEqual(ticket["items"][1]["display_label"], "1 × Menu Signature")
        self.assertEqual(ticket["items"][1]["amount_display"], "45,00 €")

        extra_labels = [line["display_label"] for line in ticket["extras"]]
        self.assertIn("2 Boulettes", extra_labels)
        self.assertIn("Caramel Liégeois", extra_labels)

        self.assertTrue(ticket["vat_summary"]["rates"])
        self.assertEqual(ticket["totals"]["grand_total_display"], "126,00 €")

