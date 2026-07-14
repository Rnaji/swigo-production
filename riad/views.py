import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction

from riad.services.table_details import build_table_details

from django.db.models import Prefetch, Case, When, IntegerField

from riad.services.workflow import get_workflow_step

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from decimal import Decimal
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import DiningOrder, Payment

from .models import DiningTable, DiningOrder, Payment

from .models import (
    Room,
    DiningTable,
    TableService,
    DiningOrder,
    GuestOrder,
    GuestChoice,
    Menu,
    MenuSection,
    ProductCategory,
    Product,
    KitchenTicket,
    KitchenTicketItem,
)


def get_next_action_label(next_status):

    labels = {
        "installed": "Installer",
        "ordering": "Prendre la commande",
        "ordered": "Valider la commande",
        "drinks_served": "Servir les boissons",
        "starters_served": "Servir les entrées",
        "starters_cleared": "Débarrasser les entrées",
        "mains_served": "Servir les plats",
        "mains_cleared": "Débarrasser les plats",
        "desserts_served": "Servir les desserts",
        "desserts_cleared": "Débarrasser les desserts",
        "coffee_served": "Servir le café",
        "coffee_cleared": "Débarrasser",
        "bill_requested": "Présenter l'addition",
        "paid": "Encaisser",
        "free": "Libérer la table",
    }

    return labels.get(next_status, "Suivant")


def get_action_icon(title):
    title = title.lower()

    if "boisson" in title:
        return "local_bar"

    if "entrée" in title:
        return "restaurant_menu"

    if "plat" in title:
        return "restaurant"

    if "dessert" in title:
        return "icecream"

    if "thé" in title or "café" in title:
        return "local_cafe"

    if "paiement" in title or "addition" in title:
        return "payments"

    if "commande" in title:
        return "edit_note"

    if "installer" in title:
        return "table_restaurant"

    return "table_restaurant"


def serialize_table_service(table, service):

    next_status = service.get_next_status()

    workflow = get_workflow_step(service.status)

    data = service.to_dict()

    data.update({
        "id": table.id,
        "numero": table.numero,
        "room": table.room.name,
        "next_status": next_status,
        "next_status_label": get_next_action_label(next_status),
        "reservation": None,

        # Affichage identique au panneau de droite
        "action": workflow["title"],
        "icon": get_action_icon(workflow["title"]),
    })

    if service.reservation:
        data["reservation"] = {
            "nom": service.reservation.nom,
            "personnes": service.reservation.personnes,
        }

    return data


def get_or_create_service(table):
    service, _ = TableService.objects.get_or_create(
        table=table,
        defaults={
            "status": "free",
            "status_started_at": timezone.now(),
        },
    )

    return service


def salle(request):
    rooms = (
        Room.objects
        .prefetch_related("tables__current_service")
        .order_by("order")
    )

    return render(request, "riad/salle.html", {
        "rooms": rooms,
    })


def install_table(request, table_id):
    table = get_object_or_404(DiningTable, id=table_id)

    service, created = TableService.objects.get_or_create(
        table=table,
        defaults={
            "status": "installed",
            "status_started_at": timezone.now(),
            "installed_at": timezone.now(),
        },
    )

    if not created:
        service.status = "installed"
        service.status_started_at = timezone.now()

        if not service.installed_at:
            service.installed_at = timezone.now()

        service.save()

    return redirect("riad:salle")


def api_table_detail(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )

    service = get_or_create_service(table)

    order = (
    DiningOrder.objects
    .filter(service=service)
    .first()
)

    return JsonResponse(
        build_table_details(table, service, order)
    )


def api_table_details(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )

    service = get_or_create_service(table)

    order = (
        DiningOrder.objects
        .filter(service=service)
        .first()
    )

    return JsonResponse(
        build_table_details(
            table,
            service,
            order,
        )
    )


def api_salle(request):
    tables = (
        DiningTable.objects
        .filter(is_active=True)
        .select_related("room")
        .order_by("room__order", "grid_y", "grid_x")
    )

    data = []

    for table in tables:
        service = get_or_create_service(table)

        order = (
            DiningOrder.objects
            .filter(service=service)
            .first()
        )

        data.append(
            build_table_details(table, service, order)
        )

    return JsonResponse({
        "tables": data,
    })


@require_POST
def api_install_table(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )

    service = get_or_create_service(table)
    service.set_status("installed")

    order = (
    DiningOrder.objects
    .filter(service=service)
    .first()
)

    return JsonResponse(
        build_table_details(table, service, order)
    )


@require_POST
def api_next_step(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )

    service = get_or_create_service(table)
    next_status = service.get_next_status()

    if next_status:
        if next_status == "free":
            DiningOrder.objects.filter(service=service).delete()

        service.set_status(next_status)

    order = (
    DiningOrder.objects
    .filter(service=service)
    .first()
)

    return JsonResponse(
        build_table_details(table, service, order)
    )

def commande_table(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)

    order, _ = DiningOrder.objects.get_or_create(service=service)

    menus = Menu.objects.filter(is_active=True).order_by("order")

    return render(request, "riad/commande.html", {
        "table": table,
        "service": service,
        "order": order,
        "menus": menus,
    })




@require_POST
@require_POST
def api_start_order(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)

    order, _ = DiningOrder.objects.get_or_create(service=service)

    payload = json.loads(request.body)
    guests = payload.get("guests", [])

    order.guests.all().delete()
    order.guests_count = len(guests)
    order.save()

    for guest_data in guests:
        menu = get_object_or_404(Menu, id=guest_data["menu_id"])

        guest = GuestOrder.objects.create(
            order=order,
            guest_number=guest_data["number"],
            menu=menu,
        )

        for choice_data in guest_data.get("choices", []):
            section = get_object_or_404(MenuSection, id=choice_data["section_id"])
            product = get_object_or_404(Product, id=choice_data["product_id"])

            GuestChoice.objects.create(
                guest=guest,
                section=section,
                product=product,
            )

    service.has_drinks = True
    service.has_starters = True
    service.has_desserts = True
    service.has_coffee = True
    service.set_status("ordered")

    return JsonResponse({
        "success": True,
        "numero": table.numero,
        "guests_count": order.guests_count,
    })


def api_menu(request, menu_id):
    menu = get_object_or_404(
        Menu.objects.prefetch_related(
            "sections__items__product"
        ),
        id=menu_id,
    )

    data = {
        "id": menu.id,
        "name": menu.name,
        "price": float(menu.price),
        "sections": [],
    }

    for section in menu.sections.filter(is_active=True).order_by("order"):

        section_data = {
            "id": section.id,
            "name": section.name,
            "choice_type": section.choice_type,
            "min_choices": section.min_choices,
            "max_choices": section.max_choices,
            "required": section.required,
            "products": [],
        }

        for item in section.items.all().order_by("order"):

            section_data["products"].append({
                "id": item.product.id,
                "name": item.product.name,
            })

        data["sections"].append(section_data)

    return JsonResponse(data)




def kitchen_view(request):
    station = request.GET.get("station", "kitchen")

    items_queryset = (
        KitchenTicketItem.objects
        .select_related("section", "product")
        .annotate(section_order=Case(
            When(section__name="Mocktail", then=0),
            When(section__name="Boisson", then=1),
            When(section__name="Eau", then=2),
            When(section__name="Entrée", then=3),
            When(section__name="Plat", then=4),
            When(section__name="Dessert", then=5),
            When(section__name="Thé / Café", then=6),
            default=99,
            output_field=IntegerField(),
        ))
        .order_by("section_order", "section__name", "product__name")
    )

    tickets = (
        KitchenTicket.objects
        .filter(
            station=station,
            status__in=["pending", "preparing", "ready"],
        )
        .select_related("table", "service", "order")
        .prefetch_related(
            Prefetch("items", queryset=items_queryset)
        )
        .order_by("sent_at")
    )

    return render(request, "riad/kitchen.html", {
        "tickets": tickets,
        "station": station,
    })


@require_POST
@transaction.atomic
def api_send_order_to_kitchen(request, numero):
    data = json.loads(request.body)

    guests_data = data.get("guests", [])
    guests_count = data.get("guests_count", len(guests_data))

    table = get_object_or_404(DiningTable, numero=numero)

    service, _ = TableService.objects.get_or_create(
        table=table,
        defaults={"status": "ordering"}
    )

    order, _ = DiningOrder.objects.update_or_create(
        service=service,
        defaults={
            "guests_count": guests_count,
            "is_sent_to_kitchen": True,
        }
    )

    order.guests.all().delete()
    order.kitchen_tickets.all().delete()

    for guest_data in guests_data:
        menu = Menu.objects.get(id=guest_data["menu_id"])

        guest_order = GuestOrder.objects.create(
    order=order,
    guest_number=guest_data["number"],
    menu=menu,
    kitchen_note=guest_data.get("note", ""),
)

        for choice_data in guest_data["choices"]:
            if choice_data["section_name"] == "Formule":
                continue

            section = MenuSection.objects.get(
                menu=menu,
                name=choice_data["section_name"],
            )

            product = Product.objects.get(
                name=choice_data["product_name"],
            )

            GuestChoice.objects.create(
            guest=guest_order,
            section=section,
            product=product,
            quantity=1,
            source="menu",
            note=choice_data.get("note", ""),
        )

    grouped = {}

    choices = (
        GuestChoice.objects
        .filter(guest__order=order)
        .select_related("section", "product", "product__category")
    )

    for choice in choices:
        section_name = choice.section.name.strip()
        product_name = choice.product.name.strip()
        category_name = choice.product.category.name.strip().lower()

        bar_categories = [
            "mocktail",
            "boisson",
            "eau",
            "dessert",
            "thé / café",
            "the / cafe",
            "thé",
            "café",
        ]

        station = "bar" if category_name in bar_categories else "kitchen"

        key = (
            station,
            section_name.lower(),
            product_name.lower(),
            choice.note.strip().lower(),
        )

        if key not in grouped:
            grouped[key] = {
    "station": station,
    "section": choice.section,
    "product": choice.product,
    "quantity": 0,
    "note": choice.note,
}

        grouped[key]["quantity"] += choice.quantity

    tickets = {}

    for item in grouped.values():
        station = item["station"]

        if station not in tickets:
            tickets[station] = KitchenTicket.objects.create(
                order=order,
                table=table,
                service=service,
                ticket_type="order",
                station=station,
                course="full",
                status="pending",
            )

        KitchenTicketItem.objects.create(
        ticket=tickets[station],
        section=item["section"],
        product=item["product"],
        quantity=item["quantity"],
        note=item["note"],
    )

    service.status = "ordered"
    service.has_starters = choices.filter(section__name="Entrée").exists()
    service.has_desserts = choices.filter(section__name="Dessert").exists()
    service.has_drinks = choices.filter(
        section__name__in=["Mocktail", "Boisson", "Eau"]
    ).exists()
    service.has_coffee = choices.filter(section__name="Thé / Café").exists()
    service.save()

    return JsonResponse({
        "success": True,
        "tickets": {
            station: ticket.id
            for station, ticket in tickets.items()
        },
    })


@require_GET
def api_products_catalog(request):
    categories = ProductCategory.objects.filter(
        is_active=True
    ).prefetch_related("products").order_by("order", "name")

    data = []

    for category in categories:
        products = category.products.filter(is_active=True).order_by("name")

        data.append({
            "id": category.id,
            "name": category.name,
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "price": str(product.price),
                }
                for product in products
            ],
        })

    return JsonResponse({"categories": data})



@require_POST
@transaction.atomic
def api_add_item(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)
    order = get_object_or_404(DiningOrder, service=service)

    payload = json.loads(request.body.decode("utf-8"))

    product = get_object_or_404(Product, id=payload.get("product_id"))
    guest_number = payload.get("guest_number")
    quantity = int(payload.get("quantity", 1))

    if guest_number == "table":
        guest_number = 1

    guest = get_object_or_404(
        GuestOrder,
        order=order,
        guest_number=int(guest_number),
    )

    section = (
        MenuSection.objects
        .filter(items__product=product)
        .first()
    )

    choices = GuestChoice.objects.filter(
        guest=guest,
        product=product,
        source="extra",
    )

    created = False

    if choices.exists():
        choice = choices.first()
        choice.quantity += quantity

        for duplicate in choices.exclude(pk=choice.pk):
            choice.quantity += duplicate.quantity
            duplicate.delete()

        choice.save()

    else:
        choice = GuestChoice.objects.create(
            guest=guest,
            section=section,
            product=product,
            quantity=quantity,
            source="extra",
        )
        created = True

    category_name = product.category.name.strip().lower()

    bar_categories = [
        "mocktail",
        "boisson",
        "eau",
        "dessert",
        "thé / café",
        "the / cafe",
        "thé",
        "café",
    ]

    station = "bar" if category_name in bar_categories else "kitchen"

    if order.is_sent_to_kitchen and section:
        ticket = KitchenTicket.objects.create(
            order=order,
            table=table,
            service=service,
            ticket_type="extra",
            station=station,
            course="full",
            status="pending",
        )

        KitchenTicketItem.objects.create(
            ticket=ticket,
            section=section,
            product=product,
            quantity=quantity,
            note="Supplément",
        )

    return JsonResponse({
        "success": True,
        "created": created,
        "product": product.name,
        "quantity": choice.quantity,
        "station": station,
    })

@require_GET
def api_product_categories(request):
    categories = (
        ProductCategory.objects
        .filter(is_active=True)
        .prefetch_related("products")
        .order_by("order", "name")
    )

    return JsonResponse({
        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "price": str(product.price),
                    }
                    for product in category.products.all()
                    if product.is_active
                ],
            }
            for category in categories
        ]
    })


def cashier_view(request, table_id):
    table = get_object_or_404(DiningTable, id=table_id)

    service = getattr(table, "current_service", None)

    if not service:
        return redirect("salle")

    order = getattr(service, "order", None)

    if not order:
        return redirect("salle")

    return render(request, "riad/cashier.html", {
        "table": table,
        "service": service,
        "order": order,
        "total": order.total_amount(),
        "paid": order.paid_amount(),
        "remaining": order.remaining_amount(),
        "payments": order.payments.all(),
    })




@require_POST
def create_payment(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON invalide"}, status=400)

    order_id = data.get("order_id")
    payments = data.get("payments", [])

    order = get_object_or_404(DiningOrder, id=order_id)

    remaining_before = order.remaining_amount()

    for payment_data in payments:
        method = payment_data.get("method")
        amount = Decimal(str(payment_data.get("amount", "0")))

        if method not in ["card", "cash"]:
            return JsonResponse({"success": False, "error": "Paiement invalide"}, status=400)

        if amount <= 0:
            continue

        if amount > remaining_before:
            amount = remaining_before

        Payment.objects.create(
            order=order,
            method=method,
            amount=amount,
        )

        remaining_before -= amount

        if remaining_before <= Decimal("0.00"):
            break

    total = order.total_amount()
    paid = order.paid_amount()
    remaining = order.remaining_amount()

    if remaining <= Decimal("0.00"):
        order.service.set_status("paid")

    return JsonResponse({
        "success": True,
        "total": float(total),
        "paid": float(paid),
        "remaining": float(max(remaining, Decimal("0.00"))),
        "payments": [
            {
                "method": payment.method,
                "method_display": payment.get_method_display(),
                "amount": float(payment.amount),
            }
            for payment in order.payments.all()
        ],
        "service_status": order.service.status,
    })