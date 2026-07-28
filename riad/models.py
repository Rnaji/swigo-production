from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
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

    task_claimed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Tâche prise en charge à",
    )

    task_claimed_extra_ticket = models.ForeignKey(
        "KitchenTicket",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claimed_server_tasks",
        verbose_name="Bon extra pris en charge",
    )

    task_claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claimed_table_tasks",
        verbose_name="Tâche prise en charge par",
    )

    bill_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Addition demandée à",
    )

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
        self.task_claimed_at = None
        self.task_claimed_extra_ticket = None
        self.task_claimed_by = None

        if new_status == "installed" and not self.installed_at:
            self.installed_at = timezone.now()

        if new_status == "paid":
            self.closed_at = timezone.now()

        if new_status == "bill_requested" and not self.bill_requested_at:
            self.bill_requested_at = timezone.now()

        if new_status == "free":
            self.installed_at = None
            self.closed_at = None
            self.bill_requested_at = None
            self.has_drinks = False
            self.has_starters = False
            self.has_desserts = False
            self.has_coffee = False
            self.task_claimed_at = None
            self.task_claimed_extra_ticket = None
            self.task_claimed_by = None

        self.save()

    def get_next_status(self, order=None):
        from riad.services.order_content import (
            compute_next_status,
            get_order_service_flags,
        )

        if order is None:
            try:
                order = self.order
            except ObjectDoesNotExist:
                order = None

        if order:
            flags = get_order_service_flags(order)
        else:
            flags = {
                "has_drinks": self.has_drinks,
                "has_starters": self.has_starters,
                "has_mains": True,
                "has_desserts": self.has_desserts,
                "has_coffee": self.has_coffee,
            }

        return compute_next_status(self.status, flags)

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
    short_name = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Nom court",
        help_text="Libellé court pour l'affichage dans le wizard.",
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    vat_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("10.00"),
    )
    is_active = models.BooleanField(default=True)
    sub_choice_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_choice_parents",
        verbose_name="Catégorie de sous-choix",
    )

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
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Terminée"),
        (STATUS_CANCELLED, "Annulée"),
    ]

    service = models.OneToOneField(
        TableService,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    guests_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Personnes présentes",
        help_text="Nombre de couverts pour les statistiques.",
    )
    is_sent_to_kitchen = models.BooleanField(default=False)
    wizard_draft = models.JSONField(null=True, blank=True)

    table_numero = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Numéro de table (archivé)",
    )
    service_started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Installation clients",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Clôture",
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Annulation",
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Paiement caisse homologuée",
    )
    bill_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Addition demandée (archivé)",
    )
    total_ttc = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    card_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    cash_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    service_period = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="midi ou soir (snapshot à la clôture)",
    )
    timeline_snapshot = models.JSONField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-completed_at", "-created_at")
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def is_completed(self):
        return self.status == self.STATUS_COMPLETED

    @property
    def display_table_numero(self):
        if self.table_numero is not None:
            return self.table_numero
        if self.service_id and self.service:
            return self.service.table.numero
        return None

    def total_amount(self):
        if self.total_ttc is not None and self.status == self.STATUS_COMPLETED:
            return self.total_ttc
        from riad.services.pricing import compute_order_total

        return compute_order_total(self)

    def paid_amount(self):
        if self.status == self.STATUS_COMPLETED:
            return self.card_amount + self.cash_amount
        from riad.services.prefetched_data import (
            PrefetchMissingError,
            get_prefetched_payments,
        )

        try:
            payments = get_prefetched_payments(self)
        except PrefetchMissingError:
            payments = list(self.payments.all())

        return sum(
            (payment.amount for payment in payments),
            Decimal("0.00"),
        )

    def remaining_amount(self):
        return self.total_amount() - self.paid_amount()

    def is_fully_paid(self):
        return self.remaining_amount() <= Decimal("0.00")

    @property
    def has_wizard_draft(self):
        return bool(self.wizard_draft) and not self.is_sent_to_kitchen

    def __str__(self):
        table_label = self.display_table_numero
        if table_label is not None:
            return f"Commande #{self.pk} - Table {table_label}"
        return f"Commande #{self.pk}"


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

    menu_applied_vat_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("10.00"),
    )

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
        ("replacement", "Remplacement"),
        ("manual_extra", "Supplément libre"),
        ("offered", "Offert"),
    ]

    STATION_CHOICES = [
        ("kitchen", "Cuisine"),
        ("bar", "Bar / Office"),
    ]

    guest = models.ForeignKey(
        GuestOrder,
        on_delete=models.CASCADE,
        related_name="choices",
        null=True,
        blank=True,
    )

    order = models.ForeignKey(
        DiningOrder,
        on_delete=models.CASCADE,
        related_name="table_level_choices",
        null=True,
        blank=True,
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
        null=True,
        blank=True,
        related_name="guest_choices",
    )

    quantity = models.PositiveIntegerField(default=1)

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="menu",
    )

    supplement_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
    )

    line_total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    label = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    station = models.CharField(
        max_length=20,
        choices=STATION_CHOICES,
        blank=True,
        default="",
    )

    replaced_product_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    note = models.CharField(
        max_length=200,
        blank=True,
    )

    applied_vat_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("section__order", "product__name")

    def __str__(self):
        name = self.label or (self.product.name if self.product else "Choix")

        if self.guest_id:
            return f"Convive {self.guest.guest_number} - {name}"

        return f"Table {self.order_id} - {name}"

    @property
    def is_table_scope(self):
        return self.guest_id is None and self.order_id is not None

    @property
    def billing_amount(self):
        from riad.services.pricing import choice_line_amount

        return choice_line_amount(self)
    
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

    @property
    def all_items_done(self):
        items = list(self.items.all())
        return bool(items) and all(item.is_done for item in items)
    
class KitchenTicketItem(models.Model):

    ticket = models.ForeignKey(
        KitchenTicket,
        on_delete=models.CASCADE,
        related_name="items",
    )

    section = models.ForeignKey(
        MenuSection,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    label = models.CharField(
        max_length=150,
        blank=True,
        default="",
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

    done_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Marqué fait à",
    )

    serve_batch_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Lot de service",
    )

    serve_claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claimed_kitchen_items",
        verbose_name="Pris en charge par",
    )

    serve_claimed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Pris en charge à",
    )

    is_served = models.BooleanField(
        default=False,
        verbose_name="Servi",
    )

    served_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Servi à",
    )

    class Meta:
        ordering = (
            "section__order",
            "product__name",
        )

    def __str__(self):
        name = self.label or (self.product.name if self.product else "Article")
        return f"{self.quantity} × {name}"
    

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

    guest_number = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"{self.order} - {self.get_method_display()} - {self.amount} €"