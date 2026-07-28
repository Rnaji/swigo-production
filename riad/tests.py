import json
from decimal import Decimal

from django.test import TestCase, TransactionTestCase
from django.utils import timezone

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

        self.order.is_sent_to_kitchen = True
        self.order.save(update_fields=["is_sent_to_kitchen", "updated_at"])

        return guest

    def create_kitchen_lines(self, section_name, products, station="kitchen", ticket_type="order"):
        from riad.models import KitchenTicket, KitchenTicketItem

        ticket = KitchenTicket.objects.create(
            order=self.order,
            table=self.table,
            service=self.service,
            ticket_type=ticket_type,
            station=station,
            course="full",
            status="pending",
        )

        section = self.sections[section_name]

        now = timezone.now()

        for product, is_done in products:
            KitchenTicketItem.objects.create(
                ticket=ticket,
                section=section,
                product=product,
                quantity=1,
                is_done=is_done,
                done_at=now if is_done else None,
            )

        return ticket

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

    def prepare_order_for_table_details(self, order=None, service=None):
        from riad.services.prefetch import (
            orders_queryset_for_details,
            prefetch_workflow_items_for_orders,
        )

        order = order or self.order
        service = service or self.service
        # Toujours recharger : les to_attr peuvent être périmés après mutation.
        order = orders_queryset_for_details(order_ids=[order.id]).first()
        if order:
            prefetch_workflow_items_for_orders(
                [order],
                services_by_order_id={order.id: service},
            )
            self.order = order
        return order

    def build_table_details_prepared(self):
        from riad.services.table_details import build_table_details

        order = self.prepare_order_for_table_details()
        return build_table_details(self.table, self.service, order)


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
        self.assertEqual(compute_next_status("mains_cleared", flags), "coffee_cleared")

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


class TimelineVisualStateTests(OrderContentTestMixin, TestCase):
    def _state(self, stage_key, status):
        self.service.status = status
        self.service.save(update_fields=["status", "updated_at"])
        sync_service_flags_from_order(self.service, self.order)

        from riad.services.timeline import get_stage_visual_state

        return get_stage_visual_state(stage_key, self.service, self.order)

    def _setup_full_menu_order(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])

    def test_starters_black_blue_green_sequence(self):
        self._setup_full_menu_order()

        self.assertEqual(self._state("starters", "drinks_served"), "active")
        self.assertEqual(self._state("starters", "starters_served"), "waiting_clear")
        self.assertEqual(self._state("starters", "starters_cleared"), "completed")
        self.assertEqual(self._state("mains", "starters_served"), "pending")
        self.assertEqual(self._state("mains", "starters_cleared"), "active")

    def test_mains_black_blue_green_sequence(self):
        self._setup_full_menu_order()

        self.assertEqual(self._state("mains", "starters_cleared"), "active")
        self.assertEqual(self._state("mains", "mains_served"), "waiting_clear")
        self.assertEqual(self._state("mains", "mains_cleared"), "completed")

    def test_desserts_black_blue_green_sequence(self):
        self._setup_full_menu_order()

        self.assertEqual(self._state("desserts", "mains_cleared"), "active")
        self.assertEqual(self._state("desserts", "desserts_served"), "waiting_clear")
        self.assertEqual(self._state("desserts", "desserts_cleared"), "completed")

    def test_coffee_black_blue_green_sequence(self):
        self._setup_full_menu_order()

        self.assertEqual(self._state("coffee", "desserts_cleared"), "active")
        self.assertEqual(self._state("coffee", "coffee_served"), "waiting_clear")
        self.assertEqual(self._state("coffee", "coffee_cleared"), "completed")

    def test_drinks_without_clear_step(self):
        self.create_table_extra("Coca-Cola")

        self.assertEqual(self._state("drinks", "ordered"), "active")
        self.assertEqual(self._state("drinks", "drinks_served"), "completed")

    def test_order_without_dessert_skips_dessert_icon(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)

        from riad.services.timeline import build_timeline

        timeline = build_timeline(self.service, self.order)
        dessert_keys = [step["key"] for step in timeline]

        self.assertNotIn("desserts", dessert_keys)
        self.assertEqual(self._state("desserts", "mains_cleared"), "pending")

    def test_order_without_starter_serves_mains_directly(self):
        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)

        self.assertEqual(self._state("starters", "ordered"), "pending")
        self.assertEqual(self._state("mains", "starters_cleared"), "active")


class ServerTaskListTests(OrderContentTestMixin, TestCase):
    def test_build_task_list_one_task_per_active_table(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)

        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines("Entrée", [
            (self.products["Salade marocaine"], True),
        ])

        tasks = build_task_list(iter_active_services_with_orders())

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["table_numero"], 99)
        self.assertIn("entrée", tasks[0]["title"].lower())

    def test_claimed_tasks_sorted_before_unclaimed(self):
        from riad.services.tasks import sort_server_tasks

        tasks = sort_server_tasks([
            {
                "claimed": False,
                "claimed_by_me": False,
                "priority_score": 100,
                "sort_timestamp": 100,
                "table_numero": 1,
            },
            {
                "claimed": True,
                "claimed_by_me": True,
                "priority_score": 300,
                "sort_timestamp": 200,
                "table_numero": 2,
            },
            {
                "claimed": False,
                "claimed_by_me": False,
                "priority_score": 10,
                "sort_timestamp": 300,
                "table_numero": 3,
            },
        ])

        self.assertTrue(tasks[0]["claimed_by_me"])
        self.assertEqual(tasks[0]["table_numero"], 2)
        self.assertEqual(tasks[1]["table_numero"], 3)
        self.assertEqual(tasks[2]["table_numero"], 1)

    def test_set_status_clears_task_claim(self):
        self.service.status = "ordered"
        self.service.task_claimed_at = timezone.now()
        self.service.save(update_fields=["status", "task_claimed_at", "updated_at"])

        self.service.set_status("drinks_served")

        self.service.refresh_from_db()
        self.assertIsNone(self.service.task_claimed_at)
        self.assertIsNone(self.service.task_claimed_by_id)

    def test_visual_state_overdue_after_five_minutes(self):
        from riad.services.tasks import get_task_visual_state

        self.service.status = "ordered"
        self.service.status_started_at = timezone.now() - timezone.timedelta(minutes=6)
        self.service.task_claimed_at = None
        self.service.save(
            update_fields=["status", "status_started_at", "task_claimed_at", "updated_at"]
        )

        self.assertEqual(get_task_visual_state(self.service), "overdue")

    def test_api_task_claim(self):
        self.service.status = "installed"
        self.service.save(update_fields=["status", "updated_at"])

        response = self.client.post(
            f"/riad/api/tasks/{self.service.id}/claim/",
            data='{"task_key":"workflow"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("/commande/?from=tasks", payload.get("redirect_url", ""))
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "ordering")
        self.assertIsNotNone(self.service.task_claimed_at)

        response = self.client.post(
            f"/riad/api/tasks/{self.service.id}/claim/",
            data='{"task_key":"workflow"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)

    def test_api_tasks_includes_take_order_for_installed_table(self):
        self.service.status = "installed"
        self.service.installed_at = timezone.now()
        self.service.save(update_fields=["status", "installed_at", "updated_at"])

        response = self.client.get("/riad/api/tasks/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        tasks = payload["tasks"]
        order_tasks = [
            task for task in tasks
            if task.get("title") == "Prendre la commande"
            and task.get("table_numero") == self.table.numero
        ]
        self.assertEqual(len(order_tasks), 1)
        task = order_tasks[0]
        self.assertTrue(task["is_order_task"])
        self.assertEqual(task["table_numero"], self.table.numero)
        self.assertIn("/commande/?from=tasks", task["commande_url"])
        self.assertEqual(payload["count"], len(tasks))

    def test_take_order_task_disappears_after_ordering_starts(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        self.service.status = "installed"
        self.service.installed_at = timezone.now()
        self.service.save(update_fields=["status", "installed_at", "updated_at"])

        installed_tasks = [
            task for task in build_task_list(iter_active_services_with_orders())
            if task.get("title") == "Prendre la commande"
        ]
        self.assertEqual(len(installed_tasks), 1)

        self.service.set_status("ordering")
        ordering_tasks = [
            task for task in build_task_list(iter_active_services_with_orders())
            if task.get("title") == "Prendre la commande"
        ]
        self.assertEqual(ordering_tasks, [])
        finalize_tasks = [
            task for task in build_task_list(iter_active_services_with_orders())
            if task.get("is_order_task")
        ]
        self.assertEqual(len(finalize_tasks), 1)
        self.assertIn("commande", finalize_tasks[0]["title"].lower())

    def test_tasks_js_syntax_has_valid_isOrderTask_guard(self):
        from pathlib import Path

        source = Path(__file__).resolve().parent.joinpath("static/riad/js/tasks.js").read_text()
        self.assertIn("if (isOrderTask(task)) {", source)
        self.assertNotRegex(source, r"(?m)^\s*if\s+isOrderTask\(")

        try:
            import esprima
        except ImportError:
            return

        esprima.parseScript(source)

    def test_take_order_task_shows_installed_since_label(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        self.service.status = "installed"
        self.service.installed_at = timezone.now() - timezone.timedelta(minutes=4)
        self.service.status_started_at = self.service.installed_at
        self.service.save(
            update_fields=[
                "status",
                "installed_at",
                "status_started_at",
                "updated_at",
            ]
        )

        tasks = build_task_list(iter_active_services_with_orders())
        order_tasks = [
            task for task in tasks
            if task.get("title") == "Prendre la commande"
        ]

        self.assertEqual(len(order_tasks), 1)
        self.assertEqual(
            order_tasks[0]["installed_since_label"],
            "👥 Clients installés depuis 4 min",
        )
        self.assertIsNotNone(order_tasks[0]["installed_at"])
        self.assertIsNone(order_tasks[0]["elapsed_label"])

    def test_take_order_task_under_one_minute(self):
        from riad.services.tasks import format_installed_since_label

        self.assertEqual(
            format_installed_since_label(30),
            "👥 Clients installés à l'instant",
        )

    def test_take_order_task_over_one_hour(self):
        from riad.services.tasks import format_installed_since_label

        self.assertEqual(
            format_installed_since_label(72 * 60),
            "👥 Clients installés depuis 1 h 12",
        )

    def test_other_tasks_do_not_show_installed_since_label(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.installed_at = timezone.now() - timezone.timedelta(hours=2)
        self.service.save(update_fields=["status", "installed_at", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        tasks = build_task_list(iter_active_services_with_orders())
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]

        self.assertEqual(len(serve_tasks), 1)
        self.assertIsNone(serve_tasks[0].get("installed_since_label"))


class ServeItemTaskTests(OrderContentTestMixin, TestCase):
    def _serve_tasks(self, **kwargs):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        return build_task_list(iter_active_services_with_orders(), **kwargs)

    def test_single_ready_line_creates_task_immediately(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
        ])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertIn("plat", serve_tasks[0]["title"].lower())
        self.assertEqual(serve_tasks[0]["items"][0]["quantity"], 1)
        self.assertEqual(serve_tasks[0]["items"][0]["name"], "Couscous Royal")
        self.assertEqual(serve_tasks[0]["task_type"], "serve_mains")
        self.assertEqual(serve_tasks[0]["table_name"], f"Table {self.table.numero}")

    def test_closed_kitchen_ticket_still_creates_serve_task(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
        ])
        ticket.status = "served"
        ticket.finished_at = timezone.now()
        ticket.save(update_fields=["status", "finished_at"])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertIn("plat", serve_tasks[0]["title"].lower())
        self.assertLess(serve_tasks[0]["priority_score"], 100)

    def test_partial_category_creates_serve_task_for_ready_lines(self):
        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, False),
        ])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 1 plat")
        self.assertEqual(len(serve_tasks[0]["item_ids"]), 1)

        details = self.build_table_details_prepared()
        self.assertEqual(details["action"], "Servir 1 plat")
        self.assertIn("en préparation", details["next_action"].get("progress_label", "").lower())

    def test_unclaimed_task_absorbs_new_ready_lines(self):
        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )
        pastilla = Product.objects.create(
            category=self.categories["Plat"],
            name="Pastilla",
            price=Decimal("16.00"),
        )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        for product in (tajine, pastilla):
            GuestChoice.objects.create(
                guest=guest,
                section=self.sections["Plat"],
                product=product,
                quantity=1,
                source="extra",
            )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, False),
            (pastilla, False),
        ])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 1 plat")

        tajine_item = ticket.items.get(product=tajine)
        tajine_item.is_done = True
        tajine_item.done_at = timezone.now()
        tajine_item.save(update_fields=["is_done", "done_at"])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 2 plats")
        self.assertEqual(len(serve_tasks[0]["item_ids"]), 2)

        pastilla_item = ticket.items.get(product=pastilla)
        pastilla_item.is_done = True
        pastilla_item.done_at = timezone.now()
        pastilla_item.save(update_fields=["is_done", "done_at"])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 3 plats")
        self.assertEqual(len(serve_tasks[0]["item_ids"]), 3)

    def test_complete_claimed_batch_does_not_serve_later_ready_lines(self):
        from django.contrib.auth.models import User
        from riad.models import KitchenTicketItem
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, False),
        ])

        user = User.objects.create_user(username="serveur_partial_batch", password="test")
        claimed, err = claim_serve_task(self.service, available_task_key("mains"), user)
        self.assertIsNone(err)

        tajine_item = ticket.items.get(product=tajine)
        tajine_item.is_done = True
        tajine_item.done_at = timezone.now()
        tajine_item.save(update_fields=["is_done", "done_at"])

        ok, err = complete_serve_task(self.service, self.order, claimed["task_key"], user)
        self.assertTrue(ok)
        self.assertIsNone(err)

        couscous = KitchenTicketItem.objects.get(product=self.products["Couscous Royal"])
        tajine_item.refresh_from_db()
        self.assertTrue(couscous.is_served)
        self.assertFalse(tajine_item.is_served)

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 1 plat")
        self.assertEqual(serve_tasks[0]["item_ids"], [tajine_item.id])

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "starters_cleared")

        user2 = User.objects.create_user(username="serveur_partial_batch2", password="test")
        claimed2, err = claim_serve_task(self.service, available_task_key("mains"), user2)
        self.assertIsNone(err)
        complete_serve_task(self.service, self.order, claimed2["task_key"], user2)

        tajine_item.refresh_from_db()
        self.assertTrue(tajine_item.is_served)
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "mains_served")

    def test_two_servers_cannot_claim_same_available_batch(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        user_a = User.objects.create_user(username="serveur_a", password="test")
        user_b = User.objects.create_user(username="serveur_b", password="test")

        first, err_a = claim_serve_task(self.service, available_task_key("mains"), user_a)
        second, err_b = claim_serve_task(self.service, available_task_key("mains"), user_b)

        self.assertIsNone(err_a)
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertIsNotNone(err_b)

    def test_kitchen_and_office_partial_ready_creates_one_serve_task(self):
        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
        ])
        guest = self.order.guests.first()
        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines(
            "Plat",
            [(self.products["Couscous Royal"], True)],
            station="kitchen",
        )
        self.create_kitchen_lines(
            "Plat",
            [(tajine, False)],
            station="office",
        )

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 1 plat")
        details = self.build_table_details_prepared()
        self.assertEqual(details["action"], "Servir 1 plat")

    def test_clear_only_after_all_lines_served(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, True),
        ])

        user = User.objects.create_user(username="serveur_clear_partial", password="test")
        claimed, _ = claim_serve_task(self.service, available_task_key("mains"), user)

        # Simuler une 2e ligne devenue prête après claim : on retire un item du lot
        # en le "déclamant" n'est pas le scénario — claim a figé les 2.
        # On valide le lot complet puis on vérifie clear.
        complete_serve_task(self.service, self.order, claimed["task_key"], user)
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "mains_served")

        tasks = self._serve_tasks()
        self.assertTrue(any("débarrasser" in task["title"].lower() for task in tasks))

    def test_complete_available_freezes_batch_without_claim(self):
        from django.contrib.auth.models import User
        from riad.models import KitchenTicketItem
        from riad.services.serve_tasks import available_task_key, complete_serve_task

        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        ticket = self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, False),
        ])

        user = User.objects.create_user(username="serveur_direct", password="test")
        ok, err = complete_serve_task(
            self.service,
            self.order,
            available_task_key("mains"),
            user,
        )
        self.assertTrue(ok)
        self.assertIsNone(err)

        couscous = KitchenTicketItem.objects.get(product=self.products["Couscous Royal"])
        tajine_item = ticket.items.get(product=tajine)
        self.assertTrue(couscous.is_served)
        self.assertFalse(tajine_item.is_served)

    def test_two_ready_lines_grouped_before_claim(self):
        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, True),
        ])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(len(serve_tasks[0]["item_ids"]), 2)
        self.assertEqual(len(serve_tasks[0]["items"]), 2)

    def test_identical_products_are_aggregated_in_items(self):
        from riad.models import KitchenTicketItem

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])
        KitchenTicketItem.objects.create(
            ticket=ticket,
            section=self.sections["Plat"],
            product=self.products["Couscous Royal"],
            quantity=1,
            is_done=True,
            done_at=timezone.now(),
        )

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(len(serve_tasks[0]["items"]), 1)
        self.assertEqual(serve_tasks[0]["items"][0]["name"], "Couscous Royal")
        self.assertEqual(serve_tasks[0]["items"][0]["quantity"], 2)

    def test_claimed_task_keeps_items_visible(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        user = User.objects.create_user(username="serveur_items", password="test")
        claimed_task, _ = claim_serve_task(self.service, available_task_key("mains"), user)

        self.assertTrue(claimed_task["claimed"])
        self.assertEqual(len(claimed_task["items"]), 1)
        self.assertEqual(claimed_task["items"][0]["name"], "Couscous Royal")

        tasks = self._serve_tasks(current_user=user)
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["items"][0]["quantity"], 1)

    def test_cancelled_kitchen_line_not_in_task(self):
        from riad.models import KitchenTicketItem

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])
        ticket.items.first().delete()

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 0)

    def test_ice_cream_choice_shows_final_product_name(self):
        self.create_guest(1, [("Dessert", "Les 2 Palmiers", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "mains_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines(
            "Dessert",
            [(self.products["Les 2 Palmiers"], True)],
            station="bar",
        )

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["items"][0]["name"], "Les 2 Palmiers")

    def test_service_note_is_exposed_but_technical_note_is_hidden(self):
        from riad.models import KitchenTicketItem

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])
        item = ticket.items.first()
        item.note = "Sans pois chiches"
        item.save(update_fields=["note"])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(serve_tasks[0]["items"][0]["note"], "Sans pois chiches")

        item.note = "Supplément"
        item.save(update_fields=["note"])
        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(serve_tasks[0]["items"][0]["note"], "")

    def test_order_task_has_no_product_items(self):
        TableService.objects.create(table=DiningTable.objects.create(room=self.room, numero=51, grid_x=3, grid_y=1), status="installed")

        tasks = self._serve_tasks()
        order_tasks = [task for task in tasks if task.get("is_order_task")]
        self.assertTrue(order_tasks)
        self.assertEqual(order_tasks[0]["items"], [])

    def test_new_ready_line_after_claim_creates_separate_task(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task

        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, False),
        ])

        user = User.objects.create_user(username="serveur_batch", password="test")
        claim_serve_task(self.service, available_task_key("mains"), user)

        tajine_item = ticket.items.get(product=tajine)
        tajine_item.is_done = True
        tajine_item.done_at = timezone.now()
        tajine_item.save(update_fields=["is_done", "done_at"])

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 2)

    def test_served_line_never_reappears(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        user = User.objects.create_user(username="serveur_done", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("mains"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        tasks = self._serve_tasks()
        serve_tasks = [task for task in tasks if task["action_type"] == "serve_items"]
        self.assertEqual(len(serve_tasks), 0)

    def test_all_mains_served_advances_to_clearing(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        user = User.objects.create_user(username="serveur_clear", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("mains"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "mains_served")
        self.service.status_started_at = timezone.now() - timezone.timedelta(minutes=20)
        self.service.save(update_fields=["status_started_at", "updated_at"])

        tasks = self._serve_tasks()
        self.assertTrue(any("débarrasser" in task["title"].lower() for task in tasks))

    def test_clearing_task_shows_served_since_label(self):
        from django.contrib.auth.models import User
        from riad.models import KitchenTicketItem
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        user = User.objects.create_user(username="serveur_clear_label", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("mains"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        KitchenTicketItem.objects.filter(ticket__order=self.order).update(
            served_at=timezone.now() - timezone.timedelta(minutes=18),
        )

        tasks = self._serve_tasks()
        clearing_tasks = [
            task for task in tasks
            if "débarrasser" in task["title"].lower() and "plat" in task["title"].lower()
        ]
        self.assertEqual(len(clearing_tasks), 1)
        self.assertEqual(clearing_tasks[0]["served_since_label"], "Plats servis depuis 18 min")
        self.assertIsNotNone(clearing_tasks[0]["served_since_at"])

    def test_main_still_preparing_blocks_clearing(self):
        tajine = Product.objects.create(
            category=self.categories["Plat"],
            name="Tajine poulet",
            price=Decimal("15.00"),
        )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        guest = self.order.guests.first()
        GuestChoice.objects.create(
            guest=guest,
            section=self.sections["Plat"],
            product=tajine,
            quantity=1,
            source="extra",
        )
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines("Plat", [
            (self.products["Couscous Royal"], True),
            (tajine, False),
        ])

        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        user = User.objects.create_user(username="serveur_partial", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("mains"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "starters_cleared")

        tasks = self._serve_tasks()
        self.assertFalse(any("débarrasser" in task["title"].lower() for task in tasks))

    def test_extra_ready_after_main_step_creates_independent_task(self):
        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "desserts_served"
        self.service.save(update_fields=["status", "updated_at"])

        self.create_kitchen_lines(
            "Dessert",
            [(self.products["Pâtisseries marocaines"], True)],
            station="bar",
            ticket_type="extra",
        )

        tasks = self._serve_tasks()
        extra_tasks = [
            task for task in tasks
            if task["action_type"] == "serve_items" and "extra" in task["title"].lower()
        ]
        self.assertEqual(len(extra_tasks), 1)

    def test_kitchen_toggle_does_not_advance_table_status(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])

        ticket = self.create_kitchen_lines("Entrée", [
            (self.products["Salade marocaine"], False),
        ])
        item = ticket.items.first()

        self.client.post(f"/riad/kitchen/item/{item.id}/toggle/")
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "drinks_served")

    def test_ready_main_before_take_order_priority(self):
        table_b = DiningTable.objects.create(room=self.room, numero=50, grid_x=2, grid_y=1)
        TableService.objects.create(table=table_b, status="installed")

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        tasks = self._serve_tasks()
        self.assertGreaterEqual(len(tasks), 2)
        self.assertEqual(tasks[0]["priority_score"], 10)

    def test_claimed_serve_task_hidden_for_other_user(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task

        user_a = User.objects.create_user(username="serveur_a2", password="test")
        user_b = User.objects.create_user(username="serveur_b2", password="test")

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        claim_serve_task(self.service, available_task_key("mains"), user_a)

        tasks_for_a = self._serve_tasks(current_user=user_a)
        tasks_for_b = self._serve_tasks(current_user=user_b)

        self.assertEqual(len(tasks_for_a), 1)
        self.assertTrue(tasks_for_a[0]["claimed_by_me"])
        self.assertEqual(len(tasks_for_b), 0)


class ServeItemTaskConcurrencyTests(OrderContentTestMixin, TransactionTestCase):
    def test_concurrent_claim_only_one_succeeds(self):
        from concurrent.futures import ThreadPoolExecutor
        from django.contrib.auth.models import User

        from riad.services.serve_tasks import available_task_key

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        user_a = User.objects.create_user(username="conc_a", password="test")
        user_b = User.objects.create_user(username="conc_b", password="test")

        def attempt_claim(user):
            response = self.client.post(
                f"/riad/api/tasks/{self.service.id}/claim/",
                data=json.dumps({"task_key": available_task_key("mains")}),
                content_type="application/json",
            )
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(attempt_claim, [user_a, user_b]))

        self.assertEqual(sorted(results), [200, 409])


class BillTaskTests(OrderContentTestMixin, TestCase):
    def _bill_tasks(self, **kwargs):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        tasks = build_task_list(iter_active_services_with_orders(), **kwargs)
        return [
            task for task in tasks
            if "addition" in task["title"].lower()
        ]

    def test_coffee_cleared_creates_bill_task(self):
        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "coffee_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        tasks = self._bill_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Apporter l'addition")
        self.assertEqual(tasks[0]["action_type"], "action")
        self.assertIsNone(tasks[0].get("pre_ticket_url"))

    def test_desserts_served_without_bill_request_has_no_bill_task(self):
        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "desserts_served"
        self.service.save(update_fields=["status", "updated_at"])

        self.assertEqual(len(self._bill_tasks()), 0)

    def test_bill_requested_has_no_bill_task(self):
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.set_status("bill_requested")
        self.service.refresh_from_db()

        self.assertEqual(len(self._bill_tasks()), 0)
        self.assertIsNotNone(self.service.bill_requested_at)

    def test_complete_bill_task_advances_to_payment_without_pre_ticket_navigation(self):
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "coffee_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        tasks_before = self._bill_tasks()
        self.assertEqual(len(tasks_before), 1)
        self.assertIsNone(tasks_before[0].get("pre_ticket_url"))
        self.assertNotEqual(tasks_before[0].get("action_type"), "open_pre_ticket")

        response = self.client.post(f"/riad/api/table/{self.table.numero}/next/")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "bill_requested")
        self.assertIsNotNone(self.service.bill_requested_at)

        self.assertEqual(data["status"], "bill_requested")
        self.assertEqual(data["next_action"]["type"], "payment")
        self.assertNotIn("pre_ticket_url", data["next_action"])
        self.assertNotEqual(data["next_action"].get("type"), "open_pre_ticket")

        # Aucune navigation automatique : le pré-ticket reste un lien manuel.
        payment_html_hint = data.get("order") or {}
        self.assertTrue(payment_html_hint.get("exists"))

        details = self.build_table_details_prepared()
        self.assertEqual(details["status"], "bill_requested")
        self.assertEqual(details["next_action"]["type"], "payment")
        self.assertNotIn("pre_ticket_url", details["next_action"])
        self.assertEqual(details["action"], "Paiement")

        self.assertEqual(len(self._bill_tasks()), 0)

        # Le pré-ticket reste une URL manuelle (identique au bouton drawer),
        # jamais renvoyée comme navigation automatique.
        pre_ticket_url = f"/riad/table/{self.table.id}/pre-ticket/"
        self.assertTrue(pre_ticket_url.endswith("/pre-ticket/"))
        self.assertNotIn("redirect", data.get("next_action") or {})
        self.assertIsNone((data.get("next_action") or {}).get("pre_ticket_url"))
        self.assertNotIn("pre-ticket", str(data.get("next_action") or {}).lower())

    def test_explicit_bill_request_via_next_step(self):
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "coffee_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        response = self.client.post(f"/riad/api/table/{self.table.numero}/next/")
        self.assertEqual(response.status_code, 200)

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "bill_requested")
        self.assertIsNotNone(self.service.bill_requested_at)

        self.assertEqual(len(self._bill_tasks()), 0)

    def test_double_bill_request_does_not_duplicate_task(self):
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "coffee_cleared"
        self.service.save(update_fields=["status", "updated_at"])

        first_count = len(self._bill_tasks())

        self.service.status_started_at = timezone.now()
        self.service.save(update_fields=["status_started_at", "updated_at"])

        second_count = len(self._bill_tasks())
        self.assertEqual(first_count, 1)
        self.assertEqual(second_count, 1)

    def test_compute_next_status_waits_on_coffee_cleared_without_auto_bill(self):
        from riad.services.order_content import compute_next_status

        flags = {
            "has_drinks": False,
            "has_starters": False,
            "has_mains": True,
            "has_desserts": False,
            "has_coffee": False,
        }

        self.assertEqual(compute_next_status("mains_cleared", flags), "coffee_cleared")
        self.assertEqual(compute_next_status("desserts_cleared", flags), "coffee_cleared")
        self.assertEqual(compute_next_status("coffee_cleared", flags), "bill_requested")


class PaymentDeleteTests(OrderContentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        from riad.models import Payment

        self.Payment = Payment
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.set_status("bill_requested")

    def test_delete_internal_payment_updates_summary(self):
        card_payment = self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("10.00"),
        )
        cash_payment = self.Payment.objects.create(
            order=self.order,
            method="cash",
            amount=Decimal("5.00"),
        )

        response = self.client.post(
            f"/riad/api/payment/{card_payment.id}/delete/",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["paid"], 5.0)
        self.assertGreater(data["remaining"], 0)
        self.assertEqual(len(data["payments"]), 1)
        self.assertEqual(data["payments"][0]["id"], cash_payment.id)
        self.assertFalse(self.Payment.objects.filter(id=card_payment.id).exists())

    def test_delete_internal_payment_blocked_after_paid(self):
        payment = self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("10.00"),
        )
        self.service.set_status("paid")

        response = self.client.post(
            f"/riad/api/payment/{payment.id}/delete/",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertTrue(self.Payment.objects.filter(id=payment.id).exists())


class PreTicketInternalTrackingTests(OrderContentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        from riad.models import Payment
        from riad.services.pre_ticket import build_internal_payment_tracking

        self.Payment = Payment
        self.build_internal_payment_tracking = build_internal_payment_tracking
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        sync_service_flags_from_order(self.service, self.order)
        self.service.set_status("bill_requested")

    def _tracking(self):
        return self.build_internal_payment_tracking(self.order)

    def test_no_payments(self):
        tracking = self._tracking()

        self.assertFalse(tracking["has_payments"])
        self.assertEqual(tracking["lines"], [])
        self.assertEqual(tracking["empty_message"], "Aucun paiement enregistré")
        self.assertEqual(tracking["paid_display"], "0,00 €")
        self.assertGreater(tracking["remaining"], 0)

    def test_full_card_payment(self):
        self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("35.00"),
        )

        tracking = self._tracking()

        self.assertEqual(len(tracking["lines"]), 1)
        self.assertEqual(tracking["lines"][0]["label"], "Carte bancaire")
        self.assertEqual(tracking["lines"][0]["amount_display"], "35,00 €")
        self.assertEqual(tracking["paid_display"], "35,00 €")
        self.assertEqual(tracking["remaining_display"], "0,00 €")

    def test_full_cash_payment(self):
        self.Payment.objects.create(
            order=self.order,
            method="cash",
            amount=Decimal("35.00"),
        )

        tracking = self._tracking()

        self.assertEqual(len(tracking["lines"]), 1)
        self.assertEqual(tracking["lines"][0]["label"], "Espèces")
        self.assertEqual(tracking["lines"][0]["amount_display"], "35,00 €")

    def test_mixed_payments(self):
        self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("20.00"),
        )
        self.Payment.objects.create(
            order=self.order,
            method="cash",
            amount=Decimal("15.00"),
        )

        tracking = self._tracking()

        self.assertEqual(len(tracking["lines"]), 2)
        self.assertEqual(tracking["lines"][0]["label"], "Carte bancaire")
        self.assertEqual(tracking["lines"][0]["amount_display"], "20,00 €")
        self.assertEqual(tracking["lines"][1]["label"], "Espèces")
        self.assertEqual(tracking["lines"][1]["amount_display"], "15,00 €")
        self.assertEqual(tracking["paid_display"], "35,00 €")
        self.assertEqual(tracking["remaining_display"], "0,00 €")

    def test_multiple_card_payments_are_aggregated(self):
        self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("30.00"),
        )
        self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("20.00"),
        )
        self.Payment.objects.create(
            order=self.order,
            method="cash",
            amount=Decimal("10.00"),
        )
        self.Payment.objects.create(
            order=self.order,
            method="cash",
            amount=Decimal("10.00"),
        )

        tracking = self._tracking()

        self.assertEqual(len(tracking["lines"]), 2)
        self.assertEqual(tracking["lines"][0]["amount_display"], "50,00 €")
        self.assertEqual(tracking["lines"][1]["amount_display"], "20,00 €")

    def test_partial_payment(self):
        self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("10.00"),
        )

        tracking = self._tracking()

        self.assertEqual(tracking["paid_display"], "10,00 €")
        self.assertGreater(tracking["remaining"], 0)

    def test_delete_payment_updates_internal_tracking_in_api(self):
        payment = self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("10.00"),
        )
        self.Payment.objects.create(
            order=self.order,
            method="cash",
            amount=Decimal("5.00"),
        )

        response = self.client.post(
            f"/riad/api/payment/{payment.id}/delete/",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        tracking = data["internal_tracking"]

        self.assertEqual(len(tracking["lines"]), 1)
        self.assertEqual(tracking["lines"][0]["label"], "Espèces")
        self.assertEqual(tracking["lines"][0]["amount_display"], "5,00 €")
        self.assertEqual(tracking["paid_display"], "5,00 €")

    def test_build_pre_ticket_includes_internal_tracking(self):
        from riad.services.pre_ticket import build_pre_ticket

        self.Payment.objects.create(
            order=self.order,
            method="card",
            amount=Decimal("35.00"),
        )

        ticket = build_pre_ticket(self.order)

        self.assertIn("internal_tracking", ticket)
        self.assertEqual(ticket["internal_tracking"]["lines"][0]["label"], "Carte bancaire")
        self.assertEqual(ticket["totals"]["grand_total_display"], "35,00 €")


class BackOfficeTests(OrderContentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        from django.contrib.auth.models import User
        from riad.models import Payment

        self.Payment = Payment
        self.admin = User.objects.create_user(
            username="admin_bo",
            password="test",
            is_staff=True,
        )
        self.server = User.objects.create_user(
            username="server_bo",
            password="test",
            is_staff=False,
        )

    def _archive_order(
        self,
        order=None,
        service=None,
        card=Decimal("0"),
        cash=Decimal("0"),
        completed_at=None,
    ):
        from riad.services.backoffice.archive import archive_completed_order

        order = order or self.order
        service = service or self.service
        service.status = "paid"
        service.installed_at = timezone.now() - timezone.timedelta(hours=1, minutes=48)
        service.closed_at = timezone.now()
        service.bill_requested_at = timezone.now() - timezone.timedelta(minutes=10)
        service.save()

        if card:
            self.Payment.objects.create(order=order, method="card", amount=card)
        if cash:
            self.Payment.objects.create(order=order, method="cash", amount=cash)

        archived = archive_completed_order(service, order)
        if completed_at:
            archived.completed_at = completed_at
            archived.save(update_fields=["completed_at"])
        return archived

    def test_completed_order_appears_in_history(self):
        from riad.services.backoffice.queries import get_completed_orders_queryset

        archived = self._archive_order(card=Decimal("50.00"), cash=Decimal("20.00"))
        qs = get_completed_orders_queryset({"period": "month"})
        self.assertIn(archived, qs)

    def test_active_order_not_in_history(self):
        from riad.services.backoffice.queries import get_completed_orders_queryset

        self.order.status = DiningOrder.STATUS_ACTIVE
        self.order.save(update_fields=["status"])
        qs = get_completed_orders_queryset({"period": "month"})
        self.assertNotIn(self.order, qs)

    def test_table_free_preserves_archived_order(self):
        self.service.status = "paid"
        self.service.installed_at = timezone.now()
        self.service.save()

        response = self.client.post(f"/riad/api/table/{self.table.numero}/next/")
        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, DiningOrder.STATUS_COMPLETED)
        self.assertIsNone(self.order.service_id)
        self.assertTrue(DiningOrder.objects.filter(pk=self.order.pk).exists())
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "free")

    def test_cancelled_order_excluded_from_revenue(self):
        from riad.services.backoffice.archive import mark_order_cancelled
        from riad.services.backoffice.queries import get_period_totals

        archived = self._archive_order(card=Decimal("70.00"))
        archived.total_ttc = Decimal("70.00")
        archived.save(update_fields=["total_ttc"])
        mark_order_cancelled(archived)

        totals = get_period_totals({"period": "month"})
        self.assertEqual(totals["revenue"], Decimal("0"))

    def test_cancelled_line_excluded_from_product_sales(self):
        from riad.services.backoffice.analytics import get_product_sales

        guest = self.create_guest(1, [("Entrée", "Salade marocaine", "menu")])
        choice = guest.choices.first()
        choice.is_cancelled = True
        choice.cancelled_at = timezone.now()
        choice.save()

        self._archive_order()
        sales = get_product_sales({"period": "month"})
        product_names = [row["name"] for row in sales["products"]]
        self.assertNotIn("Salade marocaine", product_names)

    def test_multiple_card_payments_summed(self):
        self.Payment.objects.create(order=self.order, method="card", amount=Decimal("30.00"))
        self.Payment.objects.create(order=self.order, method="card", amount=Decimal("20.00"))
        archived = self._archive_order()
        self.assertEqual(archived.card_amount, Decimal("50.00"))

    def test_multiple_cash_payments_summed(self):
        self.Payment.objects.create(order=self.order, method="cash", amount=Decimal("10.00"))
        self.Payment.objects.create(order=self.order, method="cash", amount=Decimal("15.00"))
        archived = self._archive_order()
        self.assertEqual(archived.cash_amount, Decimal("25.00"))

    def test_mixed_payment_ticket(self):
        archived = self._archive_order(
            card=Decimal("50.00"),
            cash=Decimal("20.00"),
        )
        self.assertEqual(archived.card_amount, Decimal("50.00"))
        self.assertEqual(archived.cash_amount, Decimal("20.00"))

    def test_filter_today(self):
        from riad.services.backoffice.queries import get_completed_orders_queryset

        archived = self._archive_order()
        archived.completed_at = timezone.now()
        archived.save(update_fields=["completed_at"])

        qs = get_completed_orders_queryset({"period": "today"})
        self.assertIn(archived, qs)

    def test_filter_custom_period(self):
        from datetime import datetime, time

        from riad.services.backoffice.queries import get_completed_orders_queryset

        archived = self._archive_order()
        day = timezone.localdate() - timezone.timedelta(days=3)
        archived.completed_at = timezone.make_aware(datetime.combine(day, time.min))
        archived.save(update_fields=["completed_at"])

        qs = get_completed_orders_queryset({
            "period": "custom",
            "date_from": day.strftime("%Y-%m-%d"),
            "date_to": day.strftime("%Y-%m-%d"),
        })
        self.assertIn(archived, qs)

    def test_average_ticket_calculation(self):
        from riad.services.backoffice.queries import get_period_totals

        first = self._archive_order(card=Decimal("40.00"))
        first.total_ttc = Decimal("40.00")
        first.save(update_fields=["total_ttc"])

        table2 = DiningTable.objects.create(
            room=self.room,
            numero=100,
            grid_x=2,
            grid_y=1,
        )
        service2 = TableService.objects.create(table=table2, status="paid")
        order2 = DiningOrder.objects.create(
            service=service2,
            guests_count=1,
            is_sent_to_kitchen=True,
        )
        second = self._archive_order(order=order2, service=service2, cash=Decimal("60.00"))
        second.total_ttc = Decimal("60.00")
        second.save(update_fields=["total_ttc"])

        totals = get_period_totals({"period": "month"})
        self.assertEqual(totals["tickets"], 2)
        self.assertEqual(totals["average_ticket"], Decimal("50.00"))

    def test_average_cover_calculation(self):
        from riad.services.backoffice.queries import get_period_totals

        self.order.guests_count = 4
        self.order.save(update_fields=["guests_count"])
        archived = self._archive_order(card=Decimal("80.00"))
        archived.total_ttc = Decimal("80.00")
        archived.save(update_fields=["total_ttc"])

        totals = get_period_totals({"period": "month"})
        self.assertEqual(totals["covers"], 4)
        self.assertEqual(totals["average_cover"], Decimal("20.00"))

    def test_csv_export(self):
        from riad.services.backoffice.export import export_tickets_csv

        self._archive_order(card=Decimal("50.00"), cash=Decimal("20.00"))
        content = export_tickets_csv({"period": "month"})

        self.assertTrue(content.startswith("\ufeff"))
        self.assertIn("Numéro de commande", content)
        self.assertIn(";", content)
        self.assertIn("50,00", content)
        self.assertIn("20,00", content)

    def test_backoffice_access_denied_for_server(self):
        self.client.force_login(self.server)
        response = self.client.get("/riad/backoffice/")
        self.assertEqual(response.status_code, 403)

    def test_backoffice_access_allowed_for_staff(self):
        from django.http import HttpResponse
        from django.test import RequestFactory

        from riad.permissions import backoffice_required

        @backoffice_required
        def dummy_view(request):
            return HttpResponse("ok")

        request = RequestFactory().get("/riad/backoffice/")
        request.user = self.admin
        response = dummy_view(request)
        self.assertEqual(response.status_code, 200)

    def test_ticket_history_pagination(self):
        from django.core.paginator import Paginator

        from riad.services.backoffice.queries import get_completed_orders_queryset

        for index in range(51):
            table = DiningTable.objects.create(
                room=self.room,
                numero=200 + index,
                grid_x=(index % 10) + 1,
                grid_y=(index // 10) + 2,
            )
            service = TableService.objects.create(table=table, status="paid")
            order = DiningOrder.objects.create(
                service=service,
                guests_count=1,
                is_sent_to_kitchen=True,
            )
            self._archive_order(order=order, service=service, cash=Decimal("10.00"))

        qs = get_completed_orders_queryset({"period": "month"})
        paginator = Paginator(qs, 50)
        self.assertEqual(paginator.num_pages, 2)
        self.assertEqual(len(paginator.page(1).object_list), 50)
        self.assertEqual(len(paginator.page(2).object_list), 1)

    def test_missing_timestamp_handled_gracefully(self):
        from riad.services.backoffice.analytics import get_service_time_stats

        archived = self._archive_order()
        archived.service_started_at = None
        archived.duration_seconds = None
        archived.bill_requested_at = None
        archived.save()

        stats = get_service_time_stats({"period": "month"})
        self.assertIn("Donnée indisponible", stats["install_to_order_display"])

    def test_archived_data_persists_in_database(self):
        archived = self._archive_order(card=Decimal("35.00"))
        order_id = archived.id

        reloaded = DiningOrder.objects.get(pk=order_id)
        self.assertEqual(reloaded.status, DiningOrder.STATUS_COMPLETED)
        self.assertEqual(reloaded.card_amount, Decimal("35.00"))
        self.assertIsNotNone(reloaded.timeline_snapshot)


class FlexibleGuestTests(OrderContentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.service.status = "ordering"
        self.service.save(update_fields=["status", "updated_at"])

    def _guest_payload(self, number=1):
        return {
            "number": number,
            "menu_id": self.menu.id,
            "note": "",
            "choices": [
                {
                    "section_name": "Entrée",
                    "product_name": "Salade marocaine",
                    "source": "menu",
                },
                {
                    "section_name": "Plat",
                    "product_name": "Couscous Royal",
                    "source": "menu",
                },
            ],
            "extras": [],
        }

    def test_send_kitchen_keeps_covers_separate_from_clients(self):
        from django.test import Client

        self.order.is_sent_to_kitchen = False
        self.order.save(update_fields=["is_sent_to_kitchen", "updated_at"])

        client = Client()
        response = client.post(
            f"/riad/api/table/{self.table.numero}/send-kitchen/",
            data=json.dumps({
                "guests_count": 4,
                "guests": [
                    self._guest_payload(1),
                    self._guest_payload(2),
                    self._guest_payload(3),
                ],
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.guests_count, 4)
        self.assertEqual(self.order.guests.count(), 3)

    def test_update_covers_does_not_change_clients(self):
        from django.test import Client

        guest = self.create_guest(1, [("Plat", "Couscous Royal", "menu")])

        client = Client()
        response = client.post(
            f"/riad/api/table/{self.table.numero}/covers/",
            data=json.dumps({"guests_count": 5}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.guests_count, 5)
        self.assertEqual(self.order.guests.count(), 1)
        self.assertTrue(GuestOrder.objects.filter(id=guest.id).exists())

    def test_delete_empty_guest(self):
        from django.test import Client

        guest = GuestOrder.objects.create(
            order=self.order,
            guest_number=2,
            menu=self.menu,
        )

        client = Client()
        response = client.post(
            f"/riad/api/table/{self.table.numero}/guest/delete/",
            data=json.dumps({"guest_number": 2}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(GuestOrder.objects.filter(id=guest.id).exists())

    def test_delete_guest_with_items_requires_confirmation(self):
        from django.test import Client

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])

        client = Client()
        response = client.post(
            f"/riad/api/table/{self.table.numero}/guest/delete/",
            data=json.dumps({"guest_number": 1}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertTrue(self.order.guests.filter(guest_number=1).exists())

    def test_delete_guest_with_items_after_confirmation(self):
        from django.test import Client

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])

        client = Client()
        response = client.post(
            f"/riad/api/table/{self.table.numero}/guest/delete/",
            data=json.dumps({"guest_number": 1, "confirmed": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.order.guests.filter(guest_number=1).exists())
        self.assertFalse(
            GuestChoice.objects.filter(
                guest__guest_number=1,
                is_cancelled=False,
            ).exists()
        )

    def test_late_guest_only_sends_new_kitchen_tickets(self):
        from django.test import Client
        from riad.models import KitchenTicket

        self.order.is_sent_to_kitchen = False
        self.order.save(update_fields=["is_sent_to_kitchen", "updated_at"])

        client = Client()
        first_response = client.post(
            f"/riad/api/table/{self.table.numero}/send-kitchen/",
            data=json.dumps({
                "guests_count": 2,
                "guests": [self._guest_payload(1)],
            }),
            content_type="application/json",
        )
        self.assertEqual(first_response.status_code, 200)
        tickets_before = KitchenTicket.objects.filter(order=self.order).count()

        late_response = client.post(
            f"/riad/api/table/{self.table.numero}/guest/add/",
            data=json.dumps({"guest": self._guest_payload(2)}),
            content_type="application/json",
        )

        self.assertEqual(late_response.status_code, 200)
        self.assertEqual(self.order.guests.count(), 2)
        tickets_after = KitchenTicket.objects.filter(order=self.order).count()
        self.assertGreater(tickets_after, tickets_before)
        self.assertLessEqual(tickets_after - tickets_before, 2)

    def test_backoffice_covers_use_people_present_count(self):
        from riad.services.backoffice.archive import archive_completed_order
        from riad.services.backoffice.queries import get_period_totals

        self.order.guests_count = 4
        self.order.save(update_fields=["guests_count"])
        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        self.create_guest(2, [("Plat", "Couscous Royal", "menu")])
        self.create_guest(3, [("Plat", "Couscous Royal", "menu")])

        self.service.status = "paid"
        self.service.installed_at = timezone.now()
        self.service.save()
        archived = archive_completed_order(self.service, self.order)
        archived.total_ttc = Decimal("105.00")
        archived.save(update_fields=["total_ttc"])

        totals = get_period_totals({"period": "month"})
        self.assertEqual(totals["covers"], 4)
        self.assertEqual(totals["tickets"], 1)


class StarterClearTaskTests(OrderContentTestMixin, TestCase):
    def _tasks(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        return build_task_list(iter_active_services_with_orders())

    def _starter_tasks(self, tasks):
        return [
            task for task in tasks
            if "entrée" in task["title"].lower()
        ]

    def test_resolve_workflow_does_not_jump_to_clearing_from_ordered(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "ordered"
        self.service.save(update_fields=["status", "updated_at"])

        self.assertEqual(resolve_workflow_status(self.service, self.order), "drinks_served")

    def test_undone_starter_creates_no_serve_or_clear_tasks(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], False)])

        tasks = self._starter_tasks(self._tasks())
        self.assertEqual(tasks, [])

    def test_done_but_unserved_starter_creates_serve_task_only(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        tasks = self._starter_tasks(self._tasks())
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["action_type"], "serve_items")
        self.assertIn("servir", tasks[0]["title"].lower())

    def test_recently_served_starter_creates_clear_task_immediately(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        user = User.objects.create_user(username="serveur_starter_delay", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("starters"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "starters_served")

        tasks = self._starter_tasks(self._tasks())
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]
        self.assertEqual(len(clear_tasks), 1)

    def test_served_starter_creates_clear_task(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        user = User.objects.create_user(username="serveur_starter_clear", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("starters"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()

        tasks = self._starter_tasks(self._tasks())
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]
        self.assertEqual(len(clear_tasks), 1)

    def test_cleared_starter_has_no_clear_task(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        tasks = self._starter_tasks(self._tasks())
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]
        self.assertEqual(clear_tasks, [])

    def test_inconsistent_starters_served_status_is_reconciled(self):
        from riad.services.service_category_readiness import reconcile_clearing_service_status

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], False)])

        reconciled = reconcile_clearing_service_status(self.service, self.order)
        self.service.refresh_from_db()

        self.assertTrue(reconciled)
        self.assertEqual(self.service.status, "drinks_served")
        tasks = self._starter_tasks(self._tasks())
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]
        self.assertEqual(clear_tasks, [])

    def test_table1_like_ordered_with_undone_starter_has_no_clear_task(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "ordered"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], False)])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], False)])
        self.create_kitchen_lines("Thé / Café", [(self.products["Thé à la menthe"], False)])

        tasks = self._tasks()
        self.assertFalse(any("débarrasser" in task["title"].lower() for task in tasks))
        self.assertFalse(any(
            "servir" in task["title"].lower() and "entrée" in task["title"].lower()
            for task in tasks
        ))


class StarterWorkflowEndToEndTests(OrderContentTestMixin, TestCase):
    def _tasks(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        return build_task_list(iter_active_services_with_orders())

    def _table_details(self):
        return self.build_table_details_prepared()

    def _setup_order(self):
        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])

    def test_starter_not_ready_shows_preparation_without_tasks(self):
        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], False)])

        details = self._table_details()
        tasks = self._tasks()

        self.assertEqual(details["action"], "Entrées en préparation")
        self.assertEqual(details["next_action"]["type"], "wait")
        self.assertFalse(any("entrée" in task["title"].lower() for task in tasks))

    def test_all_starters_ready_shows_serve_in_salle_and_tasks(self):
        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        details = self._table_details()
        tasks = self._tasks()
        serve_tasks = [
            task for task in tasks
            if "servir" in task["title"].lower() and "entrée" in task["title"].lower()
        ]

        self.assertEqual(details["action"], "Servir 1 entrée")
        self.assertEqual(len(serve_tasks), 1)

    def test_complete_serve_updates_items_status_and_salle(self):
        from django.contrib.auth.models import User
        from riad.models import KitchenTicketItem
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        user = User.objects.create_user(username="serveur_e2e", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("starters"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        item = KitchenTicketItem.objects.filter(ticket__order=self.order).first()

        self.assertTrue(item.is_served)
        self.assertIsNotNone(item.served_at)
        self.assertEqual(self.service.status, "starters_served")
        self.assertIsNotNone(self.service.status_started_at)

        details = self._table_details()
        tasks = self._tasks()
        serve_tasks = [
            task for task in tasks
            if "servir" in task["title"].lower() and "entrée" in task["title"].lower()
        ]

        self.assertIn("entrées servies depuis", details["action"].lower())
        self.assertEqual(serve_tasks, [])

    def test_served_starter_shows_clear_immediately_in_salle_and_tasks(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        user = User.objects.create_user(username="serveur_delay_e2e", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("starters"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        details = self._table_details()
        tasks = self._tasks()
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]

        self.assertIn("entrées servies depuis", details["action"].lower())
        self.assertEqual(details["next_action"]["title"], "Débarrasser les entrées")
        self.assertEqual(len(clear_tasks), 1)
        self.assertIsNotNone(clear_tasks[0]["served_since_label"])

    def test_clear_available_without_artificial_wait(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        user = User.objects.create_user(username="serveur_clear_e2e", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("starters"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        details = self._table_details()
        tasks = self._tasks()
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]

        self.assertEqual(details["next_action"]["title"], "Débarrasser les entrées")
        self.assertEqual(len(clear_tasks), 1)

    def test_clear_starters_advances_workflow(self):
        from riad.views import api_next_step
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task
        from django.test import RequestFactory

        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        user = User.objects.create_user(username="serveur_clear_done", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("starters"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()

        factory = RequestFactory()
        request = factory.post(f"/riad/api/table/{self.table.numero}/next/")
        request.user = user
        api_next_step(request, self.table.numero)

        self.service.refresh_from_db()
        details = self._table_details()
        tasks = self._tasks()
        clear_tasks = [task for task in tasks if "débarrasser" in task["title"].lower()]

        self.assertEqual(self.service.status, "starters_cleared")
        self.assertEqual(details["action"], "Plats en préparation")
        self.assertEqual(clear_tasks, [])

    def test_partial_starter_ready_creates_serve_task(self):
        self._setup_order()
        ticket_kitchen = self.create_kitchen_lines(
            "Entrée",
            [(self.products["Salade marocaine"], True)],
        )
        ticket_office = self.create_kitchen_lines(
            "Entrée",
            [(self.products["Salade marocaine"], False)],
            station="office",
        )
        self.assertNotEqual(ticket_kitchen.id, ticket_office.id)

        tasks = self._tasks()
        serve_tasks = [
            task for task in tasks
            if "servir" in task["title"].lower() and "entrée" in task["title"].lower()
        ]

        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["title"], "Servir 1 entrée")
        details = self._table_details()
        self.assertEqual(details["action"], "Servir 1 entrée")

    def test_all_starters_served_with_lagging_status_reconciles_salle(self):
        from riad.models import KitchenTicketItem
        from riad.services.workflow_engine import repair_workflow_inconsistencies

        self._setup_order()
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        KitchenTicketItem.objects.filter(ticket__order=self.order).update(
            is_served=True,
            served_at=timezone.now(),
        )
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])

        details = self._table_details()
        tasks = self._tasks()
        serve_tasks = [
            task for task in tasks
            if "servir" in task["title"].lower() and "entrée" in task["title"].lower()
        ]

        self.assertEqual(self.service.status, "drinks_served")
        self.assertEqual(details["action"], "Entrées servies")
        self.assertEqual(serve_tasks, [])

        repair_workflow_inconsistencies(self.service, self.order, source="test")
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "starters_served")

    def test_multiple_starters_all_ready_before_serve_task(self):
        self._setup_order()
        self.create_kitchen_lines("Entrée", [
            (self.products["Salade marocaine"], True),
            (self.products["Salade marocaine"], True),
        ])

        tasks = self._tasks()
        serve_tasks = [
            task for task in tasks
            if "servir" in task["title"].lower() and "entrée" in task["title"].lower()
        ]

        self.assertEqual(len(serve_tasks), 1)
        self.assertEqual(serve_tasks[0]["action_type"], "serve_items")


class CategoryWorkflowEndToEndTests(OrderContentTestMixin, TestCase):
    """Workflow item-level unifié pour toutes les catégories."""

    def _tasks(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        return build_task_list(iter_active_services_with_orders())

    def _table_details(self):
        return self.build_table_details_prepared()

    def _tasks_matching(self, tasks, keyword):
        return [
            task for task in tasks
            if keyword.lower() in task["title"].lower()
        ]

    def _ensure_boisson_section(self):
        from riad.models import MenuSection, MenuSectionItem

        if "Boisson" not in self.sections:
            self.sections["Boisson"] = MenuSection.objects.create(
                menu=self.menu,
                name="Boisson",
                order=10,
            )
            MenuSectionItem.objects.create(
                section=self.sections["Boisson"],
                product=self.products["Coca-Cola"],
            )

    def _setup_drink_order(self):
        self._ensure_boisson_section()
        self.create_table_extra("Coca-Cola")
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "ordered"
        self.service.save(update_fields=["status", "updated_at"])

    def test_drinks_not_ready_shows_preparation(self):
        self._setup_drink_order()
        self.create_kitchen_lines("Boisson", [(self.products["Coca-Cola"], False)])

        details = self._table_details()
        self.assertEqual(details["action"], "Boissons en préparation")
        self.assertFalse(self._tasks_matching(self._tasks(), "boisson"))

    def test_drinks_ready_to_serve_and_complete(self):
        from django.contrib.auth.models import User
        from riad.models import KitchenTicketItem
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self._setup_drink_order()
        self.create_kitchen_lines("Boisson", [(self.products["Coca-Cola"], True)])

        details = self._table_details()
        serve_tasks = self._tasks_matching(self._tasks(), "boisson")
        self.assertEqual(details["action"], "Servir 1 boisson")
        self.assertEqual(len(serve_tasks), 1)

        user = User.objects.create_user(username="serveur_drinks", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("drinks"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        item = KitchenTicketItem.objects.filter(ticket__order=self.order).first()
        details = self._table_details()

        self.assertTrue(item.is_served)
        self.assertEqual(self.service.status, "drinks_served")
        self.assertNotEqual(details["action"], "Servir 1 boisson")
        self.assertFalse(self._tasks_matching(self._tasks(), "boisson"))

    def test_mains_workflow_serve_clear(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task
        from riad.views import api_next_step
        from django.test import RequestFactory

        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        details = self._table_details()
        self.assertEqual(details["action"], "Servir 1 plat")

        user = User.objects.create_user(username="serveur_mains", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("mains"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        details = self._table_details()
        self.assertEqual(self.service.status, "mains_served")
        self.assertIn("plats servis depuis", details["action"].lower())
        clear_tasks = self._tasks_matching(self._tasks(), "débarrasser")
        self.assertEqual(details["next_action"]["title"], "Débarrasser les plats")
        self.assertEqual(len(clear_tasks), 1)

        factory = RequestFactory()
        request = factory.post(f"/riad/api/table/{self.table.numero}/next/")
        request.user = user
        api_next_step(request, self.table.numero)

        self.service.refresh_from_db()
        details = self._table_details()
        self.assertEqual(self.service.status, "mains_cleared")
        self.assertEqual(details["action"], "Servir les desserts")

    def test_desserts_workflow_serve_and_waiting_clear(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task

        self.create_guest(1, [
            ("Dessert", "Pâtisseries marocaines", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "mains_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Dessert", [(self.products["Pâtisseries marocaines"], True)])

        details = self._table_details()
        self.assertEqual(details["action"], "Servir 1 dessert")

        user = User.objects.create_user(username="serveur_desserts", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("desserts"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        details = self._table_details()
        self.assertEqual(self.service.status, "desserts_served")
        self.assertIn("desserts servis depuis", details["action"].lower())
        self.assertEqual(details["next_action"]["title"], "Débarrasser les desserts")
        self.assertTrue(self._tasks_matching(self._tasks(), "débarrasser"))

    def test_coffee_workflow_serve_clear(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import available_task_key, claim_serve_task, complete_serve_task
        from riad.views import api_next_step
        from django.test import RequestFactory

        self.create_guest(1, [
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "desserts_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Thé / Café", [(self.products["Thé à la menthe"], True)])

        details = self._table_details()
        self.assertEqual(details["action"], "Servir 1 thé/café")

        user = User.objects.create_user(username="serveur_coffee", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("coffee"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)

        self.service.refresh_from_db()
        details = self._table_details()
        self.assertEqual(self.service.status, "coffee_served")
        self.assertIn("thés / cafés servis depuis", details["action"].lower())
        self.assertEqual(details["next_action"]["title"], "Débarrasser les thés / cafés")

        factory = RequestFactory()
        request = factory.post(f"/riad/api/table/{self.table.numero}/next/")
        request.user = user
        api_next_step(request, self.table.numero)

        self.service.refresh_from_db()
        details = self._table_details()
        self.assertEqual(self.service.status, "coffee_cleared")
        self.assertEqual(details["action"], "Apporter l'addition")

    def test_lagging_mains_status_reconciles_salle(self):
        from riad.models import KitchenTicketItem
        from riad.services.workflow_engine import repair_workflow_inconsistencies

        self.create_guest(1, [
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_cleared"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], True)])

        KitchenTicketItem.objects.filter(ticket__order=self.order).update(
            is_served=True,
            served_at=timezone.now(),
        )

        details = self._table_details()
        self.assertEqual(self.service.status, "starters_cleared")
        self.assertEqual(details["action"], "Plats servis")
        self.assertFalse(self._tasks_matching(self._tasks(), "servir les plats"))

        repair_workflow_inconsistencies(self.service, self.order, source="test")
        self.service.refresh_from_db()
        self.assertEqual(self.service.status, "mains_served")


class WorkflowEngineArchitectureTests(OrderContentTestMixin, TestCase):
    def test_snapshot_shared_by_salle_and_tasks(self):
        from riad.services.workflow_engine import get_service_workflow_snapshot

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        salle_snapshot = get_service_workflow_snapshot(self.service, self.order, context="salle")
        tasks_snapshot = get_service_workflow_snapshot(self.service, self.order, context="tasks")

        self.assertEqual(salle_snapshot["phase"], tasks_snapshot["phase"])
        self.assertEqual(salle_snapshot["active_category"], "starters")

    def test_read_path_does_not_mutate_status(self):
        from riad.models import KitchenTicketItem
        from riad.services.table_details import build_table_details
        from riad.services.workflow_engine import get_service_workflow_snapshot

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])
        KitchenTicketItem.objects.filter(ticket__order=self.order).update(
            is_served=True,
            served_at=timezone.now(),
        )

        get_service_workflow_snapshot(self.service, self.order, context="read")
        self.build_table_details_prepared()
        self.service.refresh_from_db()

        self.assertEqual(self.service.status, "drinks_served")


class WorkflowExclusivityMixin:
    CATEGORY_TASK_KEYWORDS = {
        "drinks": "boisson",
        "starters": "entrée",
        "mains": "plat",
        "desserts": "dessert",
        "coffee": "thé",
    }

    def _collect_workflow_state(self):
        from riad.services.workflow_engine import get_service_workflow_snapshot
        from riad.services.table_details import build_table_details
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        order = self.prepare_order_for_table_details()
        snapshot = get_service_workflow_snapshot(
            self.service,
            order,
            context="test",
            prefetched_items=getattr(order, "prefetched_workflow_items", None),
        )
        details = build_table_details(self.table, self.service, order)
        tasks = [
            task for task in build_task_list(iter_active_services_with_orders())
            if task.get("table_numero") == self.table.numero
        ]
        return snapshot, details, tasks

    def assert_workflow_exclusivity(self, category=None):
        from riad.services.service_category_readiness import (
            PHASE_READY_TO_SERVE,
            PHASE_WAITING_KITCHEN,
            get_category_items_state,
        )

        snapshot, details, tasks = self._collect_workflow_state()
        action = (details.get("action") or "").lower()
        categories = (
            [category]
            if category
            else list(snapshot.get("category_phases", {}).keys())
        )

        for cat in categories:
            keyword = self.CATEGORY_TASK_KEYWORDS[cat]
            serve_tasks = [
                task for task in tasks
                if "servir" in task["title"].lower()
                and keyword in task["title"].lower()
            ]
            clear_tasks = [
                task for task in tasks
                if "débarrasser" in task["title"].lower()
                and keyword in task["title"].lower()
            ]
            state = get_category_items_state(self.service, self.order, cat)
            phase = snapshot["category_phases"].get(cat)

            self.assertFalse(
                serve_tasks and clear_tasks,
                f"{cat}: serve and clear tasks must not coexist",
            )

            if cat == snapshot.get("active_category"):
                if phase == PHASE_WAITING_KITCHEN:
                    self.assertNotIn(
                        "servir",
                        action,
                        f"{cat}: preparation must not show serve action",
                    )
                if phase == PHASE_READY_TO_SERVE:
                    self.assertNotIn(
                        "préparation",
                        action,
                        f"{cat}: ready must not show preparation action",
                    )

            if state["all_served"]:
                self.assertEqual(
                    serve_tasks,
                    [],
                    f"{cat}: no serve task when all items served",
                )

            if not state["all_served"]:
                self.assertEqual(
                    clear_tasks,
                    [],
                    f"{cat}: no clear task before all items served",
                )


class FullServiceWorkflowEndToEndTests(WorkflowExclusivityMixin, OrderContentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        from django.contrib.auth.models import User

        self.service.status = "free"
        self.service.save(update_fields=["status", "updated_at"])
        self.server = User.objects.create_user(username="serveur_e2e_full", password="test")

    def _ensure_boisson_section(self):
        from riad.models import MenuSection, MenuSectionItem

        if "Boisson" not in self.sections:
            self.sections["Boisson"] = MenuSection.objects.create(
                menu=self.menu,
                name="Boisson",
                order=10,
            )
            MenuSectionItem.objects.create(
                section=self.sections["Boisson"],
                product=self.products["Coca-Cola"],
            )

    def _mark_category_done(self, category):
        from riad.models import KitchenTicketItem
        from riad.services.service_category_readiness import get_category_workflow_items

        items = get_category_workflow_items(self.order, category, service=self.service)
        now = timezone.now()
        KitchenTicketItem.objects.filter(
            id__in=[item.id for item in items]
        ).update(is_done=True, done_at=now)

    def _serve_category(self, category):
        from riad.services.serve_tasks import (
            available_task_key,
            claim_serve_task,
            complete_serve_task,
        )

        task, _ = claim_serve_task(
            self.service,
            available_task_key(category),
            self.server,
        )
        complete_serve_task(self.service, self.order, task["task_key"], self.server)
        self.service.refresh_from_db()

    def _clear_current_step(self):
        from django.test import RequestFactory
        from riad.views import api_next_step

        factory = RequestFactory()
        request = factory.post(f"/riad/api/table/{self.table.numero}/next/")
        request.user = self.server
        api_next_step(request, self.table.numero)
        self.service.refresh_from_db()

    def _rewind_clear_delay(self, minutes):
        self.service.status_started_at = timezone.now() - timezone.timedelta(minutes=minutes)
        self.service.save(update_fields=["status_started_at", "updated_at"])

    def _assert_step(
        self,
        *,
        expected_status,
        expected_phase=None,
        expected_active_category=None,
        action_contains=None,
        task_title_contains=None,
        task_title_excludes=None,
        category=None,
    ):
        from riad.services.service_category_readiness import get_category_workflow_items

        self.service.refresh_from_db()
        snapshot, details, tasks = self._collect_workflow_state()

        self.assertEqual(self.service.status, expected_status)

        if expected_phase is not None:
            self.assertEqual(snapshot["phase"], expected_phase)

        if expected_active_category is not None:
            self.assertEqual(snapshot["active_category"], expected_active_category)

        if action_contains is not None:
            self.assertIn(action_contains.lower(), details["action"].lower())

        if task_title_contains is not None:
            self.assertTrue(
                any(task_title_contains.lower() in task["title"].lower() for task in tasks),
                f"Expected task containing {task_title_contains!r}, got {[t['title'] for t in tasks]}",
            )

        if task_title_excludes is not None:
            self.assertFalse(
                any(task_title_excludes.lower() in task["title"].lower() for task in tasks),
                f"Unexpected task containing {task_title_excludes!r}",
            )

        if category:
            items = get_category_workflow_items(self.order, category, service=self.service)
            self.assertTrue(items, f"Expected kitchen items for {category}")

        self.assert_workflow_exclusivity(category or expected_active_category)

    def test_full_table_journey_install_to_paid(self):
        from riad.services.service_category_readiness import (
            PHASE_READY_TO_CLEAR,
            PHASE_READY_TO_SERVE,
            PHASE_SERVED_WAITING_CLEAR,
            PHASE_WAITING_KITCHEN,
            get_category_workflow_items,
        )

        self.service.set_status("installed")
        self._assert_step(expected_status="installed", action_contains="commande")

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
            ("Dessert", "Pâtisseries marocaines", "menu"),
            ("Thé / Café", "Thé à la menthe", "menu"),
        ])
        self._ensure_boisson_section()
        self.create_table_extra("Coca-Cola")
        sync_service_flags_from_order(self.service, self.order)
        self.service.set_status("ordering")
        self._assert_step(expected_status="ordering", action_contains="commande")

        self.service.set_status("ordered")
        self.create_kitchen_lines("Boisson", [(self.products["Coca-Cola"], False)])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], False)])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], False)])
        self.create_kitchen_lines("Dessert", [(self.products["Pâtisseries marocaines"], False)])
        self.create_kitchen_lines("Thé / Café", [(self.products["Thé à la menthe"], False)])

        self._assert_step(
            expected_status="ordered",
            expected_phase=PHASE_WAITING_KITCHEN,
            expected_active_category="drinks",
            action_contains="préparation",
            category="drinks",
        )

        self._mark_category_done("drinks")
        self._assert_step(
            expected_status="ordered",
            expected_phase=PHASE_READY_TO_SERVE,
            expected_active_category="drinks",
            action_contains="servir 1 boisson",
            task_title_contains="boisson",
            category="drinks",
        )

        self._serve_category("drinks")
        drinks_items = get_category_workflow_items(self.order, "drinks", service=self.service)
        self.assertTrue(all(item.is_served for item in drinks_items))
        self._assert_step(
            expected_status="drinks_served",
            expected_phase=PHASE_WAITING_KITCHEN,
            expected_active_category="starters",
            action_contains="préparation",
            category="starters",
        )

        self._mark_category_done("starters")
        self._assert_step(
            expected_status="drinks_served",
            expected_phase=PHASE_READY_TO_SERVE,
            expected_active_category="starters",
            action_contains="servir 1 entrée",
            task_title_contains="entrée",
            category="starters",
        )

        self._serve_category("starters")
        starter_items = get_category_workflow_items(self.order, "starters", service=self.service)
        self.assertTrue(all(item.is_served and item.served_at for item in starter_items))
        self._assert_step(
            expected_status="starters_served",
            expected_phase=PHASE_READY_TO_CLEAR,
            expected_active_category="starters",
            action_contains="entrées servies depuis",
            task_title_contains="débarrasser",
            category="starters",
        )
        self._clear_current_step()
        self._assert_step(
            expected_status="starters_cleared",
            expected_phase=PHASE_WAITING_KITCHEN,
            expected_active_category="mains",
            action_contains="préparation",
            category="mains",
        )

        self._mark_category_done("mains")
        self._assert_step(
            expected_status="starters_cleared",
            expected_phase=PHASE_READY_TO_SERVE,
            expected_active_category="mains",
            action_contains="servir 1 plat",
            task_title_contains="plat",
            category="mains",
        )
        self._serve_category("mains")
        self._assert_step(
            expected_status="mains_served",
            expected_phase=PHASE_READY_TO_CLEAR,
            expected_active_category="mains",
            action_contains="plats servis depuis",
            task_title_contains="débarrasser",
            category="mains",
        )
        self._clear_current_step()
        self._assert_step(
            expected_status="mains_cleared",
            expected_phase=PHASE_WAITING_KITCHEN,
            expected_active_category="desserts",
            category="desserts",
        )

        self._mark_category_done("desserts")
        self._serve_category("desserts")
        self._assert_step(
            expected_status="desserts_served",
            expected_phase=PHASE_READY_TO_CLEAR,
            expected_active_category="desserts",
            action_contains="desserts servis depuis",
            task_title_contains="débarrasser",
            category="desserts",
        )
        self._clear_current_step()
        self._assert_step(
            expected_status="desserts_cleared",
            expected_phase=PHASE_WAITING_KITCHEN,
            expected_active_category="coffee",
            category="coffee",
        )

        self._mark_category_done("coffee")
        self._serve_category("coffee")
        self._assert_step(
            expected_status="coffee_served",
            expected_phase=PHASE_READY_TO_CLEAR,
            expected_active_category="coffee",
            action_contains="thés / cafés servis depuis",
            task_title_contains="débarrasser",
            category="coffee",
        )
        self._clear_current_step()
        self._assert_step(expected_status="coffee_cleared", action_contains="addition")

        self._clear_current_step()
        self._assert_step(expected_status="bill_requested", action_contains="paiement")

        self.service.set_status("paid")
        _, _, tasks = self._collect_workflow_state()
        self.assertEqual(self.service.status, "paid")
        self.assertFalse(
            any(
                "servir" in task["title"].lower()
                or "débarrasser" in task["title"].lower()
                for task in tasks
            )
        )


class WorkflowPerformanceTests(OrderContentTestMixin, TestCase):
    def _seed_active_table(self, numero, *, with_order=False, with_kitchen=False):
        table = DiningTable.objects.create(
            room=self.room,
            numero=numero,
            grid_x=numero % 10,
            grid_y=numero // 10,
        )
        service = TableService.objects.create(table=table, status="ordered")
        order = None
        if with_order:
            order = DiningOrder.objects.create(
                service=service,
                guests_count=1,
                is_sent_to_kitchen=with_kitchen,
            )
            if with_kitchen:
                self.create_guest_on_order(
                    order,
                    1,
                    [("Entrée", "Salade marocaine", "menu")],
                )
                self.create_kitchen_lines_on_order(
                    order,
                    "Entrée",
                    [(self.products["Salade marocaine"], False)],
                )
        return table, service, order

    def create_guest_on_order(self, order, guest_number, choices_spec):
        from riad.models import GuestOrder

        guest = GuestOrder.objects.create(
            order=order,
            guest_number=guest_number,
            menu=self.menu,
        )
        for section_name, product_name, source in choices_spec:
            GuestChoice.objects.create(
                guest=guest,
                section=self.sections[section_name],
                product=self.products[product_name],
                source=source,
                quantity=1,
            )

    def create_kitchen_lines_on_order(self, order, section_name, product_specs):
        from riad.models import KitchenTicket, KitchenTicketItem

        ticket = KitchenTicket.objects.create(
            order=order,
            service=order.service,
            table=order.service.table,
            status="preparing",
            sent_at=timezone.now(),
        )
        section = self.sections[section_name]
        for product, is_done in product_specs:
            KitchenTicketItem.objects.create(
                ticket=ticket,
                section=section,
                product=product,
                is_done=is_done,
                done_at=timezone.now() if is_done else None,
            )

    def _count_queries(self, callback):
        from django.db import connection, reset_queries
        from django.test.utils import override_settings

        with override_settings(DEBUG=True):
            reset_queries()
            callback()
            return len(connection.queries)

    def _prepare_order_for_details(self, order, service):
        from riad.services.prefetch import (
            load_order_for_details,
            prefetch_workflow_items_for_orders,
        )

        order = load_order_for_details(order)
        prefetch_workflow_items_for_orders(
            [order],
            services_by_order_id={order.id: service},
        )
        return order

    def test_build_table_details_zero_queries_when_prefetched(self):
        from riad.services.table_details import build_table_details

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], False)])

        order = self._prepare_order_for_details(self.order, self.service)
        queries = self._count_queries(
            lambda: build_table_details(self.table, self.service, order)
        )
        self.assertEqual(queries, 0)

    def test_workflow_snapshot_zero_queries_when_prefetched(self):
        from riad.services.workflow_engine import get_service_workflow_snapshot

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])
        self.create_kitchen_lines("Plat", [(self.products["Couscous Royal"], False)])

        order = self._prepare_order_for_details(self.order, self.service)
        queries = self._count_queries(
            lambda: get_service_workflow_snapshot(
                self.service,
                order,
                prefetched_items=order.prefetched_workflow_items,
            )
        )
        self.assertEqual(queries, 0)

    def test_salle_scales_for_1_5_21_tables(self):
        from django.test import Client

        client = Client()
        self.table.is_active = False
        self.table.save(update_fields=["is_active"])

        created = []
        for offset in range(21):
            created.append(
                self._seed_active_table(
                    801 + offset,
                    with_order=True,
                    with_kitchen=True,
                )
            )

        def activate(count):
            for index, (table, _service, _order) in enumerate(created):
                table.is_active = index < count
                table.save(update_fields=["is_active"])

        activate(1)
        q1 = self._count_queries(lambda: client.get("/riad/api/salle/"))
        activate(5)
        q5 = self._count_queries(lambda: client.get("/riad/api/salle/"))
        activate(21)
        q21 = self._count_queries(lambda: client.get("/riad/api/salle/"))

        self.assertLessEqual(q1, 25)
        self.assertLessEqual(q5, 40)
        self.assertLessEqual(q21, 80)
        self.assertLess(q5, q1 * 4)
        self.assertLess(q21, q1 * 12)

        print(f"PERF salle tables=1 queries={q1}")
        print(f"PERF salle tables=5 queries={q5}")
        print(f"PERF salle tables=21 queries={q21}")

    def test_task_list_does_not_double_snapshot(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        self.create_guest(1, [("Entrée", "Salade marocaine", "menu")])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])

        queries = self._count_queries(
            lambda: build_task_list(iter_active_services_with_orders())
        )
        self.assertLessEqual(queries, 30)

    def test_api_salle_endpoint_query_budget(self):
        from django.test import Client

        for numero in range(901, 906):
            self._seed_active_table(numero, with_order=True, with_kitchen=True)

        client = Client()
        queries = self._count_queries(
            lambda: client.get("/riad/api/salle/")
        )
        self.assertLessEqual(queries, 40)


class ClearTaskImmediateTests(OrderContentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        from django.contrib.auth.models import User

        self.server = User.objects.create_user(username="clear_immediate", password="test")

    def _serve_starters(self):
        from riad.services.serve_tasks import (
            available_task_key,
            claim_serve_task,
            complete_serve_task,
        )

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "drinks_served"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Entrée", [(self.products["Salade marocaine"], True)])
        task, _ = claim_serve_task(
            self.service,
            available_task_key("starters"),
            self.server,
        )
        complete_serve_task(self.service, self.order, task["task_key"], self.server)
        self.service.refresh_from_db()

    def test_clear_task_visible_immediately_after_serve(self):
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        self._serve_starters()
        tasks = build_task_list(iter_active_services_with_orders())
        clear_tasks = [
            task for task in tasks
            if "débarrasser" in task["title"].lower() and "entrée" in task["title"].lower()
        ]
        self.assertEqual(len(clear_tasks), 1)

    def test_no_artificial_wait_before_clear(self):
        from riad.services.service_category_readiness import (
            PHASE_READY_TO_CLEAR,
            get_category_phase,
            is_clear_task_allowed,
        )

        self._serve_starters()
        self.assertTrue(is_clear_task_allowed(self.service, self.order))
        self.assertEqual(
            get_category_phase(self.service, self.order, "starters"),
            PHASE_READY_TO_CLEAR,
        )

    def test_served_since_label_uses_max_served_at(self):
        from riad.models import KitchenTicketItem
        from riad.services.service_category_readiness import build_served_since_info

        self.create_guest(1, [
            ("Entrée", "Salade marocaine", "menu"),
            ("Plat", "Couscous Royal", "menu"),
        ])
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "starters_served"
        self.service.save(update_fields=["status", "updated_at"])
        ticket = self.create_kitchen_lines("Entrée", [
            (self.products["Salade marocaine"], True),
            (self.products["Salade marocaine"], True),
        ])
        items = list(KitchenTicketItem.objects.filter(ticket=ticket).order_by("id"))
        older = timezone.now() - timezone.timedelta(minutes=10)
        newer = timezone.now() - timezone.timedelta(minutes=2)
        items[0].is_served = True
        items[0].served_at = older
        items[0].save(update_fields=["is_served", "served_at"])
        items[1].is_served = True
        items[1].served_at = newer
        items[1].save(update_fields=["is_served", "served_at"])

        info = build_served_since_info("starters", items)
        self.assertEqual(info["served_since_label"], "Entrées servies depuis 2 min")
        self.assertTrue(info["served_since_at"].startswith(newer.isoformat()[:19]))

    def test_served_since_less_than_one_minute(self):
        from riad.services.service_category_readiness import format_served_since_label

        self.assertEqual(
            format_served_since_label("Desserts servis", 20),
            "Desserts servis depuis moins d'une minute",
        )

    def test_clear_disappears_after_debarrassage(self):
        from django.test import RequestFactory
        from riad.services.tasks import build_task_list, iter_active_services_with_orders
        from riad.views import api_next_step

        self._serve_starters()
        factory = RequestFactory()
        request = factory.post(f"/riad/api/table/{self.table.numero}/next/")
        request.user = self.server
        api_next_step(request, self.table.numero)

        self.service.refresh_from_db()
        details = self.build_table_details_prepared()
        tasks = build_task_list(iter_active_services_with_orders())
        clear_tasks = [
            task for task in tasks
            if "débarrasser" in task["title"].lower() and "entrée" in task["title"].lower()
        ]

        self.assertEqual(self.service.status, "starters_cleared")
        self.assertEqual(clear_tasks, [])
        self.assertNotIn("servies depuis", details["action"].lower())

    def test_drinks_have_no_clear_task(self):
        from django.contrib.auth.models import User
        from riad.services.serve_tasks import (
            available_task_key,
            claim_serve_task,
            complete_serve_task,
        )
        from riad.services.tasks import build_task_list, iter_active_services_with_orders

        if "Boisson" not in self.sections:
            from riad.models import MenuSection, MenuSectionItem

            self.sections["Boisson"] = MenuSection.objects.create(
                menu=self.menu,
                name="Boisson",
                order=10,
            )
            MenuSectionItem.objects.create(
                section=self.sections["Boisson"],
                product=self.products["Coca-Cola"],
            )

        self.create_guest(1, [("Plat", "Couscous Royal", "menu")])
        self.create_table_extra("Coca-Cola")
        sync_service_flags_from_order(self.service, self.order)
        self.service.status = "ordered"
        self.service.save(update_fields=["status", "updated_at"])
        self.create_kitchen_lines("Boisson", [(self.products["Coca-Cola"], True)])

        user = User.objects.create_user(username="clear_drinks", password="test")
        task, _ = claim_serve_task(self.service, available_task_key("drinks"), user)
        complete_serve_task(self.service, self.order, task["task_key"], user)
        self.service.refresh_from_db()

        tasks = build_task_list(iter_active_services_with_orders())
        self.assertEqual(self.service.status, "drinks_served")
        self.assertFalse(
            any(
                "débarrasser" in task["title"].lower() and "boisson" in task["title"].lower()
                for task in tasks
            )
        )


class PrefetchImportArchitectureTests(TestCase):
    def test_prefetch_and_prefetched_data_imports_any_order(self):
        from riad.services.prefetch import prefetch_orders_for_table_details
        from riad.services.prefetched_data import get_prefetched_guest_choices

        self.assertTrue(callable(prefetch_orders_for_table_details))
        self.assertTrue(callable(get_prefetched_guest_choices))

    def test_prefetched_data_then_prefetch_imports(self):
        from riad.services.prefetched_data import get_prefetched_guest_choices
        from riad.services.prefetch import prefetch_orders_for_table_details

        self.assertTrue(callable(get_prefetched_guest_choices))
        self.assertTrue(callable(prefetch_orders_for_table_details))

    def test_prefetched_data_has_no_service_imports(self):
        import riad.services.prefetched_data as module

        source = open(module.__file__, encoding="utf-8").read()
        self.assertNotIn("riad.services.summary", source)
        self.assertNotIn("riad.services.pricing", source)
        self.assertNotIn("riad.services.table_details", source)
        self.assertNotIn("riad.services.workflow_context", source)
        self.assertNotIn("riad.services.prefetch", source)
