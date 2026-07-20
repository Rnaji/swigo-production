import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction

from riad.services.pre_ticket import build_pre_ticket
from riad.services.vat import MENU_VAT_RATE, parse_vat_rate
from riad.services.table_details import build_table_details

from riad.services.pricing import (
    choice_line_amount,
    choice_display_name,
    compute_order_total,
    compute_guest_total,
    compute_guest_paid_amount,
    build_order_billing,
)
from riad.services.replacement_rules import compute_replacement_supplement
from riad.services.kitchen_dispatch import (
    build_ticket_items_from_choices,
    send_choice_to_kitchen,
)
from riad.services.kitchen_routing import station_for_product
from riad.services.order_content import sync_service_flags_from_order

from django.db.models import Prefetch, Case, When, IntegerField, Q

from riad.services.workflow import get_workflow_step
from riad.services.order_content import resolve_workflow_status

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
import json

from decimal import Decimal
import json

from django.http import JsonResponse, Http404
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
    MenuSectionItem,
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
    order = DiningOrder.objects.filter(service=service).first()
    next_status = service.get_next_status(order)
    workflow_status = resolve_workflow_status(service, order)
    workflow = get_workflow_step(workflow_status)

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


def order_is_locked(order):
    return order.service.status == "paid"


def parse_decimal_amount(value, default="0"):
    if value is None or value == "":
        return Decimal(default)
    return Decimal(str(value).replace(",", ".").strip())


ADD_ITEM_CATEGORIES = {
    "Boisson",
    "Jus",
    "Eau",
    "Mocktail",
    "Dessert",
    "Coupe glacée",
    "Thé / Café",
}


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
    order = DiningOrder.objects.filter(service=service).first()

    if order:
        sync_service_flags_from_order(service, order)

    next_status = service.get_next_status(order)

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
def api_save_wizard_draft(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "JSON invalide."},
            status=400,
        )

    draft = payload.get("draft")
    if not isinstance(draft, dict):
        return JsonResponse(
            {"success": False, "error": "Brouillon invalide."},
            status=400,
        )

    order, _ = DiningOrder.objects.get_or_create(service=service)

    if order.is_sent_to_kitchen:
        return JsonResponse(
            {"success": False, "error": "Commande déjà envoyée en cuisine."},
            status=400,
        )

    if service.status == "installed":
        service.set_status("ordering")
    elif service.status != "ordering":
        return JsonResponse(
            {"success": False, "error": "Table non en prise de commande."},
            status=400,
        )

    guest_count = int(draft.get("guest_count") or 0)
    order.wizard_draft = draft
    order.guests_count = guest_count
    order.save(update_fields=["wizard_draft", "guests_count", "updated_at"])

    return JsonResponse({"success": True})


@require_POST
@transaction.atomic
def api_cancel_order(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)

    if service.status != "ordering":
        return JsonResponse(
            {
                "success": False,
                "error": "Cette table n'est pas en prise de commande.",
            },
            status=400,
        )

    DiningOrder.objects.filter(service=service).delete()
    service.set_status("installed")

    return JsonResponse({
        "success": True,
        "redirect": "/riad/salle/",
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

        for item in section.items.select_related("product__sub_choice_category").all().order_by("order"):
            product = item.product
            product_data = {
                "id": product.id,
                "name": product.name,
                "short_name": product.short_name,
            }

            if product.sub_choice_category_id:
                product_data["sub_choices"] = [
                    {
                        "id": sub_product.id,
                        "name": sub_product.name,
                        "short_name": sub_product.short_name,
                    }
                    for sub_product in Product.objects.filter(
                        category_id=product.sub_choice_category_id,
                        is_active=True,
                    ).order_by("name")
                ]

            section_data["products"].append(product_data)

        data["sections"].append(section_data)

    mocktails = Product.objects.filter(
        category__name="Mocktail",
        is_active=True,
    ).order_by("name")

    coupes = Product.objects.filter(
        category__name="Coupe glacée",
        is_active=True,
    ).order_by("name")

    data["replacement_options"] = {
        "mocktails": [
            {
                "id": product.id,
                "name": product.name,
                "short_name": product.short_name,
            }
            for product in mocktails
        ],
        "coupes": [
            {
                "id": product.id,
                "name": product.name,
                "short_name": product.short_name,
            }
            for product in coupes
        ],
        "has_coupe_choice": MenuSectionItem.objects.filter(
            section__menu=menu,
            section__name="Dessert",
            product__name="Coupe de glace au choix",
        ).exists(),
    }

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
def api_toggle_kitchen_item(request, item_id):
    item = get_object_or_404(
        KitchenTicketItem.objects.select_related("ticket"),
        id=item_id,
    )

    item.is_done = not item.is_done
    item.save(update_fields=["is_done"])

    ticket = item.ticket
    items_qs = KitchenTicketItem.objects.filter(ticket_id=ticket.id)
    all_done = items_qs.exists() and not items_qs.filter(is_done=False).exists()

    return JsonResponse({
        "success": True,
        "item_id": item.id,
        "is_done": item.is_done,
        "ticket_id": ticket.id,
        "all_items_done": all_done,
    })


@require_POST
def api_mark_all_ticket_items(request, ticket_id):
    data = json.loads(request.body) if request.body else {}
    done = bool(data.get("done", True))

    ticket = get_object_or_404(KitchenTicket, id=ticket_id)
    ticket.items.update(is_done=done)

    items_qs = KitchenTicketItem.objects.filter(ticket_id=ticket.id)
    all_done = items_qs.exists() and not items_qs.filter(is_done=False).exists()

    return JsonResponse({
        "success": True,
        "ticket_id": ticket.id,
        "all_items_done": all_done,
        "done": done,
    })


@require_POST
def api_close_kitchen_ticket(request, ticket_id):
    ticket = get_object_or_404(KitchenTicket, id=ticket_id)

    ticket.status = "served"
    ticket.finished_at = timezone.now()
    ticket.save(update_fields=["status", "finished_at"])

    return JsonResponse({
        "success": True,
        "ticket_id": ticket.id,
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

    existing_order = DiningOrder.objects.filter(service=service).first()
    if existing_order and existing_order.is_sent_to_kitchen:
        return JsonResponse(
            {
                "success": False,
                "error": "Cette commande a déjà été envoyée en cuisine.",
            },
            status=400,
        )

    order, _ = DiningOrder.objects.update_or_create(
        service=service,
        defaults={
            "guests_count": guests_count,
            "is_sent_to_kitchen": True,
            "wizard_draft": None,
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
            menu_applied_vat_rate=MENU_VAT_RATE,
        )

        for choice_data in guest_data["choices"]:
            if choice_data["section_name"] == "Formule":
                continue

            section = MenuSection.objects.get(
                menu=menu,
                name=choice_data["section_name"],
            )

            sub_choice_product_name = choice_data.get("sub_choice_product_name")
            if sub_choice_product_name:
                product = Product.objects.get(name=sub_choice_product_name)
            else:
                product = Product.objects.get(name=choice_data["product_name"])

            note = choice_data.get("note", "").strip()

            replaced_product_name = (choice_data.get("replaced_product_name") or "").strip()
            source = choice_data.get("source", "menu")
            supplement_amount = parse_decimal_amount(
                choice_data.get("supplement_amount", "0")
            )

            if replaced_product_name and replaced_product_name != product.name:
                supplement_amount = compute_replacement_supplement(
                    menu,
                    section.name,
                    replaced_product_name,
                    product,
                )
                if supplement_amount > 0:
                    source = "replacement"
                else:
                    source = "menu"
                    supplement_amount = Decimal("0")
                    replaced_product_name = ""
            else:
                source = "menu"
                supplement_amount = Decimal("0")
                replaced_product_name = ""

            GuestChoice.objects.create(
                guest=guest_order,
                section=section,
                product=product,
                quantity=1,
                source=source,
                supplement_amount=supplement_amount,
                replaced_product_name=replaced_product_name,
                note=note,
                applied_vat_rate=(
                    product.vat_rate
                    if source == "replacement" and supplement_amount > 0
                    else None
                ),
            )

        for extra_data in guest_data.get("extras", []):
            extra_source = extra_data.get("source")

            if extra_source == "extra":
                product = Product.objects.get(id=extra_data["product_id"])
                section = (
                    MenuSection.objects
                    .filter(items__product=product)
                    .first()
                )
                quantity = int(extra_data.get("quantity", 1))

                GuestChoice.objects.create(
                    guest=guest_order,
                    section=section,
                    product=product,
                    quantity=quantity,
                    source="extra",
                    applied_vat_rate=product.vat_rate,
                )

            elif extra_source == "manual_extra":
                label = (extra_data.get("label") or "").strip()
                if not label:
                    continue

                try:
                    manual_vat_rate = parse_vat_rate(extra_data.get("vat_rate"))
                except ValueError:
                    manual_vat_rate = MENU_VAT_RATE

                GuestChoice.objects.create(
                    guest=guest_order,
                    section=None,
                    product=None,
                    quantity=1,
                    source="manual_extra",
                    label=label,
                    line_total=parse_decimal_amount(extra_data.get("line_total")),
                    station=extra_data.get("station", "kitchen"),
                    applied_vat_rate=manual_vat_rate,
                )

    choices = (
        GuestChoice.objects
        .filter(
            Q(guest__order=order) | Q(order=order, guest__isnull=True)
        )
        .select_related("section", "product", "product__category")
    )

    product_items, manual_items = build_ticket_items_from_choices(choices)

    tickets = {}

    for item in product_items:
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

    for item in manual_items:
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
            section=None,
            product=None,
            label=item["label"],
            quantity=item["quantity"],
            note=item["note"],
        )

    service.status = "ordered"
    sync_service_flags_from_order(service, order)
    service.save(update_fields=["status", "updated_at"])

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
        is_active=True,
        name__in=ADD_ITEM_CATEGORIES,
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
                    "vat_rate": str(product.vat_rate),
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

    if order_is_locked(order):
        return JsonResponse(
            {"success": False, "error": "Commande déjà réglée."},
            status=403,
        )

    payload = json.loads(request.body.decode("utf-8"))

    product = get_object_or_404(Product, id=payload.get("product_id"))
    quantity = int(payload.get("quantity", 1))

    if quantity < 1:
        return JsonResponse(
            {"success": False, "error": "Quantité invalide."},
            status=400,
        )

    if not order.is_sent_to_kitchen:
        return JsonResponse(
            {
                "success": False,
                "error": "Les extras de table sont disponibles après validation de la commande.",
            },
            status=400,
        )

    section = (
        MenuSection.objects
        .filter(items__product=product)
        .first()
    )

    choices = GuestChoice.objects.filter(
        order=order,
        guest__isnull=True,
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
            order=order,
            guest=None,
            section=section,
            product=product,
            quantity=quantity,
            source="extra",
            applied_vat_rate=product.vat_rate,
        )
        created = True

    if order.is_sent_to_kitchen:
        station = station_for_product(product)
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

    sync_service_flags_from_order(service, order)

    return JsonResponse({
        "success": True,
        "created": created,
        "product": product.name,
        "quantity": choice.quantity,
        "station": station_for_product(product),
        "total": float(compute_order_total(order)),
    })


@require_POST
@transaction.atomic
def api_add_manual_extra(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)
    order = get_object_or_404(DiningOrder, service=service)

    if order_is_locked(order):
        return JsonResponse(
            {"success": False, "error": "Commande déjà réglée."},
            status=403,
        )

    payload = json.loads(request.body.decode("utf-8"))

    label = (payload.get("label") or "").strip()
    quantity = int(payload.get("quantity", 1))
    line_total = parse_decimal_amount(payload.get("line_total"))
    station = payload.get("station", "kitchen")
    note = (payload.get("note") or "").strip()

    if not label:
        return JsonResponse(
            {"success": False, "error": "Intitulé obligatoire."},
            status=400,
        )

    if quantity < 1:
        return JsonResponse(
            {"success": False, "error": "Quantité invalide."},
            status=400,
        )

    if line_total < Decimal("0.00"):
        return JsonResponse(
            {"success": False, "error": "Prix invalide."},
            status=400,
        )

    if station not in ("kitchen", "bar"):
        return JsonResponse(
            {"success": False, "error": "Destination invalide."},
            status=400,
        )

    if not order.is_sent_to_kitchen:
        return JsonResponse(
            {
                "success": False,
                "error": "Les extras de table sont disponibles après validation de la commande.",
            },
            status=400,
        )

    try:
        vat_rate = parse_vat_rate(payload.get("vat_rate"))
    except ValueError as exc:
        return JsonResponse(
            {"success": False, "error": str(exc)},
            status=400,
        )

    choice = GuestChoice.objects.create(
        order=order,
        guest=None,
        section=None,
        product=None,
        quantity=quantity,
        source="manual_extra",
        label=label,
        line_total=line_total,
        station=station,
        note=note,
        applied_vat_rate=vat_rate,
    )

    if order.is_sent_to_kitchen:
        send_choice_to_kitchen(order, table, service, choice)

    sync_service_flags_from_order(service, order)

    return JsonResponse({
        "success": True,
        "choice_id": choice.id,
        "label": choice.label,
        "quantity": choice.quantity,
        "line_total": float(choice.line_total),
        "station": station,
        "total": float(compute_order_total(order)),
    })


@require_POST
@transaction.atomic
def api_delete_choice(request, numero, choice_id):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)
    order = get_object_or_404(DiningOrder, service=service)

    if order_is_locked(order):
        return JsonResponse(
            {"success": False, "error": "Commande déjà réglée."},
            status=403,
        )

    choice = get_object_or_404(
        GuestChoice,
        Q(id=choice_id)
        & (Q(guest__order=order) | Q(order=order, guest__isnull=True)),
    )

    if choice.source not in ("extra", "manual_extra"):
        return JsonResponse(
            {"success": False, "error": "Ce choix ne peut pas être supprimé ici."},
            status=400,
        )

    choice.delete()

    sync_service_flags_from_order(service, order)

    return JsonResponse({
        "success": True,
        "total": float(compute_order_total(order)),
    })

@require_GET
def api_product_categories(request):
    categories = (
        ProductCategory.objects
        .filter(is_active=True, name__in=ADD_ITEM_CATEGORIES)
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
    return pre_ticket_view(request, table_id)


def pre_ticket_view(request, table_id):
    table = get_object_or_404(DiningTable, id=table_id)

    service = getattr(table, "current_service", None)

    if not service:
        return redirect("/riad/salle/")

    order = getattr(service, "order", None)

    if not order:
        return redirect("/riad/salle/")

    pre_ticket = build_pre_ticket(order)

    return render(request, "riad/pre_ticket.html", {
        "table": table,
        "service": service,
        "order": order,
        "pre_ticket": pre_ticket,
        "paid": order.paid_amount(),
        "remaining": order.remaining_amount(),
    })


@require_POST
def api_mark_paid_external_cashier(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)

    if service.status not in ("bill_requested", "paid"):
        return JsonResponse(
            {
                "success": False,
                "error": "Cette table n'est pas en phase d'addition.",
            },
            status=400,
        )

    order = DiningOrder.objects.filter(service=service).first()
    if not order:
        return JsonResponse(
            {"success": False, "error": "Aucune commande pour cette table."},
            status=400,
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    service.set_status("paid")

    return JsonResponse({
        "success": True,
        "status": service.status,
        "operational_note": payload.get("note", ""),
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
        guest_number = payment_data.get("guest_number")

        if method not in ["card", "cash"]:
            return JsonResponse({"success": False, "error": "Paiement invalide"}, status=400)

        if amount <= 0:
            continue

        if guest_number is not None:
            guest_number = int(guest_number)
            guest = order.guests.filter(guest_number=guest_number).first()

            if not guest:
                return JsonResponse(
                    {"success": False, "error": "Convive introuvable."},
                    status=400,
                )

            guest_remaining = (
                compute_guest_total(guest) - compute_guest_paid_amount(order, guest_number)
            )

            if amount > guest_remaining:
                return JsonResponse(
                    {
                        "success": False,
                        "error": (
                            f"Le montant ({amount:.2f} €) dépasse le reste à payer "
                            f"pour ce convive ({guest_remaining:.2f} €)."
                        ),
                    },
                    status=400,
                )

        if amount > remaining_before:
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        f"Le montant ({amount:.2f} €) dépasse le reste à payer "
                        f"({remaining_before:.2f} €)."
                    ),
                },
                status=400,
            )

        Payment.objects.create(
            order=order,
            method=method,
            amount=amount,
            guest_number=guest_number if guest_number is not None else None,
        )

        remaining_before -= amount

        if remaining_before <= Decimal("0.00"):
            break

    total = order.total_amount()
    paid = order.paid_amount()
    remaining = order.remaining_amount()
    billing = build_order_billing(order)

    return JsonResponse({
        "success": True,
        "total": float(total),
        "paid": float(paid),
        "remaining": float(max(remaining, Decimal("0.00"))),
        "guests_total": float(billing["guests_total"]),
        "table_extras_total": float(billing["table_extras_total"]),
        "guest_billing": [
            {
                "guest_number": item["guest_number"],
                "total": float(item["total"]),
                "paid": float(item["paid"]),
                "remaining": float(item["remaining"]),
                "is_paid": item["is_paid"],
            }
            for item in billing["guests"]
        ],
        "payments": [
            {
                "method": payment.method,
                "method_display": payment.get_method_display(),
                "amount": float(payment.amount),
                "guest_number": payment.guest_number,
            }
            for payment in order.payments.all()
        ],
        "service_status": order.service.status,
    })