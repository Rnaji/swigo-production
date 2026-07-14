from django.db import models
from django.utils import timezone
from .constants import SERVICE_STATUS
from decimal import Decimal

class Room(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        ordering = ("order",)
        verbose_name = "Salle"
        verbose_name_plural = "Salles"

    def __str__(self):
        return self.name


class DiningTable(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="tables",
        verbose_name="Salle",
    )

    numero = models.PositiveIntegerField(
        unique=True,
        verbose_name="Numéro",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )

    grid_x = models.PositiveSmallIntegerField(
    default=1,
    verbose_name="Colonne"
    )

    grid_y = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Rangée"
    )

    class Meta:
        ordering = (
            "room__order",
            "grid_y",
            "grid_x",
        )
        verbose_name = "Table"
        verbose_name_plural = "Tables"
        constraints = [
            models.UniqueConstraint(
                fields=["room", "grid_x", "grid_y"],
                name="unique_table_position",
            ),
        ]

    def __str__(self):
        return f"Table {self.numero}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("reserved", "Réservée"),
        ("installed", "Clients installés"),
        ("cancelled", "Annulée"),
        ("finished", "Terminée"),
    ]

    table = models.ForeignKey(
        DiningTable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservations",
    )
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=30, blank=True)
    personnes = models.PositiveIntegerField(default=2)
    date_heure = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="reserved",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_heure"]
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"{self.nom} - {self.personnes} pers - {self.date_heure:%d/%m/%Y %H:%M}"


class TableService(models.Model):
    STATUS_CHOICES = [
        ("free", "Libre"),
        ("reserved", "Réservée"),
        ("installed", "Clients installés"),
        ("ordering", "Prise de commande en cours"),
        ("ordered", "Commande prise"),
        ("drinks_served", "Boissons servies"),
        ("starters_served", "Entrées servies"),
        ("starters_cleared", "Entrées débarrassées"),
        ("mains_served", "Plats servis"),
        ("mains_cleared", "Plats débarrassés"),
        ("desserts_served", "Desserts servis"),
        ("desserts_cleared", "Desserts débarrassés"),
        ("coffee_served", "Thé/Café servis"),
        ("coffee_cleared", "Thé/Café débarrassés"),
        ("bill_requested", "Addition demandée"),
        ("paid", "Addition réglée"),
    ]

    table = models.OneToOneField(
        DiningTable,
        on_delete=models.CASCADE,
        related_name="current_service",
    )

    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="free",
    )

    status_started_at = models.DateTimeField(default=timezone.now)
    installed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    has_drinks = models.BooleanField(default=False)
    has_starters = models.BooleanField(default=False)
    has_desserts = models.BooleanField(default=False)
    has_coffee = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["table__numero"]
        verbose_name = "Service de table"
        verbose_name_plural = "Services de table"

    def __str__(self):
        return f"{self.table} - {self.get_status_display()}"

    def set_status(self, new_status):
        self.status = new_status
        self.status_started_at = timezone.now()

        if new_status == "installed" and not self.installed_at:
            self.installed_at = timezone.now()

        if new_status == "paid":
            self.closed_at = timezone.now()

        if new_status == "free":
            self.reservation = None
            self.installed_at = None
            self.closed_at = None
            self.has_drinks = False
            self.has_starters = False
            self.has_desserts = False
            self.has_coffee = False

        self.save()

    def get_next_status(self):
        steps = [
            "free",
            "installed",
            "ordering",
            "ordered",
            "drinks_served",
            "starters_served",
            "starters_cleared",
            "mains_served",
            "mains_cleared",
            "desserts_served",
            "desserts_cleared",
            "coffee_served",
            "coffee_cleared",
            "bill_requested",
            "paid",
            "free",
        ]

        optional_steps = {
            "drinks_served": self.has_drinks,
            "starters_served": self.has_starters,
            "starters_cleared": self.has_starters,
            "desserts_served": self.has_desserts,
            "desserts_cleared": self.has_desserts,
            "coffee_served": self.has_coffee,
            "coffee_cleared": self.has_coffee,
        }

        try:
            current_index = steps.index(self.status)
        except ValueError:
            return None

        for next_status in steps[current_index + 1:]:
            if next_status in optional_steps and not optional_steps[next_status]:
                continue

            return next_status

        return None

    @property
    def config(self):
        return SERVICE_STATUS.get(self.status, SERVICE_STATUS["free"])

    @property
    def label(self):
        return self.config["label"]

    @property
    def action(self):
        return self.config["action"]

    @property
    def icon(self):
        return self.config["icon"]

    @property
    def target_seconds(self):
        return self.config["target"]

    @property
    def elapsed_seconds(self):
        if self.status in ["free", "reserved"]:
            return 0

        return int(
            (timezone.now() - self.status_started_at).total_seconds()
        )

    @property
    def elapsed_text(self):
        if self.status in ["free", "reserved"]:
            return ""

        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60

        return f"{minutes:02d}:{seconds:02d}"

    @property
    def progress(self):
        if not self.target_seconds:
            return 0

        return int(
            (self.elapsed_seconds / self.target_seconds) * 100
        )

    @property
    def alert(self):
        if not self.target_seconds:
            return "none"

        ratio = self.elapsed_seconds / self.target_seconds

        if ratio < 0.75:
            return "normal"

        if ratio < 1:
            return "warning"

        return "danger"

    def to_dict(self):
        return {
            "status": self.status,
            "label": self.label,
            "action": self.action,
            "icon": self.icon,
            "elapsed_seconds": self.elapsed_seconds,
            "elapsed_text": self.elapsed_text,
            "target_seconds": self.target_seconds,
            "progress": self.progress,
            "alert": self.alert,
        }
    
class ProductCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "Catégorie produit"
        verbose_name_plural = "Catégories produits"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("category__order", "name")
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "price")
        verbose_name = "Menu"
        verbose_name_plural = "Menus"

    def __str__(self):
        return f"{self.name} - {self.price} €"


class MenuSection(models.Model):
    CHOICE_TYPES = [
        ("single", "Un seul choix"),
        ("multiple", "Choix multiples"),
        ("boolean", "Oui / Non"),
    ]

    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    name = models.CharField(max_length=80)

    order = models.PositiveIntegerField(default=0)

    required = models.BooleanField(default=True)

    choice_type = models.CharField(
        max_length=20,
        choices=CHOICE_TYPES,
        default="single",
    )

    min_choices = models.PositiveSmallIntegerField(default=1)

    max_choices = models.PositiveSmallIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("menu__order", "order")
        verbose_name = "Section de menu"
        verbose_name_plural = "Sections de menu"

    def __str__(self):
        return f"{self.menu.name} - {self.name}"


class MenuSectionItem(models.Model):
    section = models.ForeignKey(
        MenuSection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("section__order", "order")
        verbose_name = "Produit de section"
        verbose_name_plural = "Produits de section"

    def __str__(self):
        return f"{self.section} : {self.product.name}"
    
class DiningOrder(models.Model):
    service = models.OneToOneField(
        TableService,
        on_delete=models.CASCADE,
        related_name="order",
    )
    guests_count = models.PositiveSmallIntegerField(default=0)
    is_sent_to_kitchen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_amount(self):
        total = Decimal("0.00")

        for guest in self.guests.all():
            if guest.menu:
                total += guest.menu.price

            for choice in guest.choices.filter(source="extra"):
                total += choice.product.price * choice.quantity

        return total

    def paid_amount(self):
        return sum(
            payment.amount for payment in self.payments.all()
        )

    def remaining_amount(self):
        return self.total_amount() - self.paid_amount()

    def is_fully_paid(self):
        return self.remaining_amount() <= Decimal("0.00")

    def __str__(self):
        return f"Commande {self.service.table}"


class GuestOrder(models.Model):
    order = models.ForeignKey(
        DiningOrder,
        on_delete=models.CASCADE,
        related_name="guests",
    )

    guest_number = models.PositiveIntegerField()

    menu = models.ForeignKey(
        Menu,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="guest_orders",
    )

    kitchen_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["guest_number"]
        unique_together = ("order", "guest_number")

    def __str__(self):
        if self.menu:
            return f"Convive {self.guest_number} - {self.menu.name}"
        return f"Convive {self.guest_number} - Aucun menu"


class GuestChoice(models.Model):
    SOURCE_CHOICES = [
        ("menu", "Menu"),
        ("extra", "Supplément"),
        ("offered", "Offert"),
    ]

    guest = models.ForeignKey(
        GuestOrder,
        on_delete=models.CASCADE,
        related_name="choices",
    )

    section = models.ForeignKey(
        MenuSection,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="guest_choices",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="guest_choices",
    )

    quantity = models.PositiveIntegerField(default=1)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="menu",
    )

    note = models.CharField(
        max_length=200,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("section__order", "product__name")

    def __str__(self):
        return f"Convive {self.guest.guest_number} - {self.product.name}"
    
class KitchenTicket(models.Model):

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("preparing", "En préparation"),
        ("ready", "Prêt"),
        ("served", "Servi"),
    ]

    TICKET_TYPE_CHOICES = [
        ("order", "Commande"),
        ("extra", "Supplément"),
    ]

    STATION_CHOICES = [
        ("kitchen", "Cuisine"),
        ("bar", "Bar / Office"),
    ]

    COURSE_CHOICES = [
        ("starter", "Entrées"),
        ("main", "Plats"),
        ("dessert", "Desserts"),
        ("drinks", "Boissons"),
        ("coffee", "Thé / Café"),
        ("full", "Commande complète"),
    ]

    order = models.ForeignKey(
        DiningOrder,
        on_delete=models.CASCADE,
        related_name="kitchen_tickets",
    )

    table = models.ForeignKey(
        DiningTable,
        on_delete=models.CASCADE,
        related_name="kitchen_tickets",
        null=True,
        blank=True,
    )

    service = models.ForeignKey(
        TableService,
        on_delete=models.CASCADE,
        related_name="kitchen_tickets",
        null=True,
        blank=True,
    )

    ticket_type = models.CharField(
        max_length=20,
        choices=TICKET_TYPE_CHOICES,
        default="order",
    )

    station = models.CharField(
        max_length=20,
        choices=STATION_CHOICES,
        default="kitchen",
    )

    course = models.CharField(
        max_length=20,
        choices=COURSE_CHOICES,
        default="full",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    sent_at = models.DateTimeField(
        auto_now_add=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-sent_at",)
        verbose_name = "Bon de préparation"
        verbose_name_plural = "Bons de préparation"

    def __str__(self):

        station = "🍳 Cuisine" if self.station == "kitchen" else "🥤 Bar"

        if self.ticket_type == "extra":
            title = "Supplément"
        else:
            title = "Commande"

        if self.table:
            return f"{station} - {title} - Table {self.table.numero}"

        return f"{station} - {title}"
    
class KitchenTicketItem(models.Model):

    ticket = models.ForeignKey(
        KitchenTicket,
        on_delete=models.CASCADE,
        related_name="items",
    )

    section = models.ForeignKey(
        MenuSection,
        on_delete=models.PROTECT,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    note = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    is_done = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = (
            "section__order",
            "product__name",
        )

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"
    

class Payment(models.Model):
    METHOD_CHOICES = [
        ("card", "Carte bancaire"),
        ("cash", "Espèces"),
    ]

    order = models.ForeignKey(
        DiningOrder,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"{self.order} - {self.get_method_display()} - {self.amount} €"