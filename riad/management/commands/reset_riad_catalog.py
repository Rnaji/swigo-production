from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from riad.models import (
    DiningOrder,
    GuestChoice,
    GuestOrder,
    KitchenTicket,
    KitchenTicketItem,
    Menu,
    MenuSection,
    MenuSectionItem,
    Payment,
    Product,
    ProductCategory,
    TableService,
)


class Command(BaseCommand):
    help = (
        "Supprime les commandes de test et l'ancien catalogue Riad, "
        "sans toucher aux salles, tables, réservations ni utilisateurs."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirme la suppression destructive des commandes et du catalogue.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError(
                "Commande destructive non exécutée.\n"
                "Pour lancer le reset, exécutez exactement :\n"
                "python manage.py reset_riad_catalog --confirm"
            )

        deleted = {}

        deleted["kitchen_ticket_items"] = KitchenTicketItem.objects.all().delete()[0]
        deleted["kitchen_tickets"] = KitchenTicket.objects.all().delete()[0]
        deleted["payments"] = Payment.objects.all().delete()[0]
        deleted["guest_choices"] = GuestChoice.objects.all().delete()[0]
        deleted["guest_orders"] = GuestOrder.objects.all().delete()[0]
        deleted["dining_orders"] = DiningOrder.objects.all().delete()[0]

        services_reset = TableService.objects.update(
            status="free",
            reservation=None,
            installed_at=None,
            closed_at=None,
            has_drinks=False,
            has_starters=False,
            has_desserts=False,
            has_coffee=False,
        )

        deleted["menu_section_items"] = MenuSectionItem.objects.all().delete()[0]
        deleted["menu_sections"] = MenuSection.objects.all().delete()[0]
        deleted["menus"] = Menu.objects.all().delete()[0]
        deleted["products"] = Product.objects.all().delete()[0]
        deleted["product_categories"] = ProductCategory.objects.all().delete()[0]

        self.stdout.write(self.style.WARNING("Reset Riad terminé."))
        self.stdout.write(f"Services de table remis à 'free' : {services_reset}")

        for label, count in deleted.items():
            self.stdout.write(f"- {label} supprimés : {count}")

        self.stdout.write(
            self.style.SUCCESS(
                "Étape suivante : python manage.py seed_riad_menu"
            )
        )
