import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction

from riad.services.pre_ticket import build_pre_ticket, build_internal_payment_tracking
from riad.services.vat import MENU_VAT_RATE, parse_vat_rate
from riad.services.table_details import build_table_details
from riad.services.perf import log_endpoint_perf
from riad.services.prefetch import (
    load_order_for_details,
    prefetch_orders_for_table_details,
    prefetch_workflow_items_for_orders,
)

from riad.services.pricing import (
    choice_line_amount,
    choice_display_name,
    compute_order_total,
    compute_guest_total,
    compute_guest_paid_amount,
    build_order_billing,
)
from riad.services.replacement_rules import compute_replacement_supplement
from riad.services.guest_orders import (
    create_guest_from_payload,
    delete_or_cancel_guest,
    get_next_guest_number,
    send_guest_choices_to_kitchen,
)
from riad.services.kitchen_dispatch import (
    build_ticket_items_from_choices,
    send_choice_to_kitchen,
)
from riad.services.kitchen_routing import station_for_product
from riad.services.order_content import sync_service_flags_from_order
from riad.services.tasks import (
    build_task_list,
    iter_active_services_with_orders,
    serialize_serve_item_task,
    serialize_workflow_task,
)
from riad.services.serve_tasks import (
    claim_serve_task,
    complete_serve_task,
    is_serve_task_key,
    release_serve_task,
)
from riad.services.serve_tasks import mark_item_ready, mark_item_not_ready

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
    Payment,
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

        # Affichage identique au panneau de droite
        "action": workflow["title"],
        "icon": get_action_icon(workflow["title"]),
    })

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


def tasks_view(request):
    return render(request, "riad/tasks.html")


@require_GET
@log_endpoint_perf("tasks")
def api_tasks(request):
    tasks = build_task_list(
        iter_active_services_with_orders(),
        current_user=request.user,
    )

    return JsonResponse({
        "tasks": tasks,
        "count": len(tasks),
    })


@require_POST
def api_task_claim(request, service_id):
    service = get_object_or_404(
        TableService.objects.select_related("table", "table__room"),
        id=service_id,
    )

    if service.status in {"free", "reserved"}:
        return JsonResponse(
            {"success": False, "error": "Cette table n'a pas de tâche active."},
            status=400,
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    task_key = payload.get("task_key", "workflow")

    if is_serve_task_key(task_key):
        task, error = claim_serve_task(service, task_key, request.user)
        if error:
            status = 409 if "plus disponible" in error else 400
            return JsonResponse({"success": False, "error": error}, status=status)

        order = DiningOrder.objects.filter(service=service).first()
        return JsonResponse({
            "success": True,
            "task": serialize_serve_item_task(
                service,
                task,
                current_user=request.user,
            ),
        })

    if service.task_claimed_at:
        return JsonResponse(
            {"success": False, "error": "Cette tâche est déjà prise en charge."},
            status=409,
        )

    service.task_claimed_at = timezone.now()
    service.task_claimed_extra_ticket = None
    service.task_claimed_by = (
        request.user if request.user.is_authenticated else None
    )
    service.save(
        update_fields=[
            "task_claimed_at",
            "task_claimed_extra_ticket",
            "task_claimed_by",
            "updated_at",
        ]
    )

    order = DiningOrder.objects.filter(service=service).first()
    redirect_url = None

    if service.status in ("installed", "ordering"):
        redirect_url = f"/riad/table/{service.table.numero}/commande/?from=tasks"
        if service.status == "installed":
            service.status = "ordering"
            service.status_started_at = timezone.now()
            service.save(
                update_fields=[
                    "status",
                    "status_started_at",
                    "task_claimed_at",
                    "task_claimed_extra_ticket",
                    "task_claimed_by",
                    "updated_at",
                ]
            )

    task = serialize_workflow_task(service, order, current_user=request.user)

    return JsonResponse({
        "success": True,
        "task": task,
        "redirect_url": redirect_url,
    })


@require_POST
def api_task_release(request, service_id):
    service = get_object_or_404(TableService, id=service_id)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    task_key = payload.get("task_key", "workflow")

    if is_serve_task_key(task_key):
        success, error = release_serve_task(service, task_key, request.user)
        if not success:
            status = 403 if error and "autre serveur" in error else 400
            return JsonResponse({"success": False, "error": error}, status=status)
        return JsonResponse({"success": True})

    if not service.task_claimed_at:
        return JsonResponse(
            {"success": False, "error": "Cette tâche n'est pas prise en charge."},
            status=400,
        )

    if request.user.is_authenticated:
        if service.task_claimed_by_id and service.task_claimed_by_id != request.user.id:
            return JsonResponse(
                {"success": False, "error": "Cette tâche est prise par un autre serveur."},
                status=403,
            )

    service.task_claimed_at = None
    service.task_claimed_extra_ticket = None
    service.task_claimed_by = None
    service.save(
        update_fields=[
            "task_claimed_at",
            "task_claimed_extra_ticket",
            "task_claimed_by",
            "updated_at",
        ]
    )

    return JsonResponse({"success": True})


@require_POST
@log_endpoint_perf("task_complete")
def api_task_complete(request, service_id):
    service = get_object_or_404(
        TableService.objects.select_related("table", "table__room"),
        id=service_id,
    )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    task_key = payload.get("task_key")
    if not task_key or not is_serve_task_key(task_key):
        return JsonResponse(
            {"success": False, "error": "Tâche de service invalide."},
            status=400,
        )

    order = DiningOrder.objects.filter(service=service).first()
    success, error = complete_serve_task(service, order, task_key, request.user)
    if not success:
        status = 403 if error and "autre serveur" in error else 400
        return JsonResponse({"success": False, "error": error}, status=status)

    return JsonResponse({"success": True})


@require_POST
def api_task_serve_extra(request, ticket_id):
    ticket = get_object_or_404(
        KitchenTicket.objects.select_related("service", "order"),
        id=ticket_id,
        ticket_type="extra",
    )

    service = ticket.service
    if not service:
        return JsonResponse(
            {"success": False, "error": "Service introuvable."},
            status=400,
        )

    from riad.services.serve_tasks import extra_batch_task_key, extra_available_task_key

    batch_id = None
    first_item = ticket.items.filter(is_done=True, is_served=False).first()
    if first_item and first_item.serve_batch_id:
        batch_id = first_item.serve_batch_id
        task_key = extra_batch_task_key(batch_id)
    else:
        task_key = extra_available_task_key(ticket.id)
        task, error = claim_serve_task(service, task_key, request.user)
        if error:
            return JsonResponse({"success": False, "error": error}, status=400)
        task_key = task["task_key"]

    order = ticket.order
    success, error = complete_serve_task(service, order, task_key, request.user)
    if not success:
        return JsonResponse({"success": False, "error": error}, status=400)

    return JsonResponse({"success": True, "ticket_id": ticket.id})


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


@log_endpoint_perf("table_detail")
def api_table_detail(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )

    service = get_or_create_service(table)

    order = load_order_for_details(
        DiningOrder.objects.filter(service=service).first()
    )
    if order:
        prefetch_workflow_items_for_orders(
            [order],
            services_by_order_id={order.id: service},
        )

    return JsonResponse(
        build_table_details(table, service, order)
    )


@log_endpoint_perf("table_details")
def api_table_details(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )

    service = get_or_create_service(table)

    order = load_order_for_details(
        DiningOrder.objects.filter(service=service).first()
    )
    if order:
        prefetch_workflow_items_for_orders(
            [order],
            services_by_order_id={order.id: service},
        )

    return JsonResponse(
        build_table_details(
            table,
            service,
            order,
        )
    )


@log_endpoint_perf("salle")
def api_salle(request):
    tables = (
        DiningTable.objects
        .filter(is_active=True)
        .select_related("room")
        .order_by("room__order", "grid_y", "grid_x")
    )
    table_list = list(tables)
    table_ids = [table.id for table in table_list]

    from riad.models import TableService

    services_by_table_id = {
        service.table_id: service
        for service in TableService.objects.filter(table_id__in=table_ids)
    }

    missing_table_ids = [
        table.id for table in table_list if table.id not in services_by_table_id
    ]
    for table_id in missing_table_ids:
        table = next(item for item in table_list if item.id == table_id)
        services_by_table_id[table_id] = get_or_create_service(table)

    service_ids = [service.id for service in services_by_table_id.values()]
    orders = prefetch_orders_for_table_details(service_ids=service_ids)
    orders_by_service_id = {order.service_id: order for order in orders}

    data = []

    for table in table_list:
        service = services_by_table_id[table.id]
        order = orders_by_service_id.get(service.id)

        data.append(
            build_table_details(
                table,
                service,
                order,
            )
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

    order = load_order_for_details(
        DiningOrder.objects.filter(service=service).first()
    )
    if order:
        prefetch_workflow_items_for_orders(
            [order],
            services_by_order_id={order.id: service},
        )

    return JsonResponse(
        build_table_details(table, service, order)
    )


@require_POST
@transaction.atomic
@log_endpoint_perf("next_step")
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
        from riad.services.order_content import CLEARING_STATUSES
        from riad.services.service_category_readiness import (
            CLEARING_STATUS_TO_CATEGORY,
            get_category_items_state,
        )

        if next_status in CLEARING_STATUSES and order:
            category = CLEARING_STATUS_TO_CATEGORY.get(next_status)
            if category:
                state = get_category_items_state(service, order, category)
                if not state["all_done"] or not state["all_served"]:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": (
                                "Impossible d'avancer : tous les articles de cette "
                                "catégorie doivent être prêts et servis."
                            ),
                        },
                        status=409,
                    )

        if next_status == "free" and order:
            from riad.services.backoffice.archive import archive_completed_order

            archive_completed_order(service, order)

        service.set_status(next_status)

    order = load_order_for_details(
        DiningOrder.objects.filter(service=service).first()
    )
    if order:
        prefetch_workflow_items_for_orders(
            [order],
            services_by_order_id={order.id: service},
        )

    return JsonResponse(
        build_table_details(table, service, order)
    )

def commande_table(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)

    order, _ = DiningOrder.objects.get_or_create(service=service)

    menus = Menu.objects.filter(is_active=True).order_by("order")
    add_guest_mode = request.GET.get("mode") == "add_guest"

    if order.is_sent_to_kitchen and not add_guest_mode:
        return redirect(f"/riad/salle/?table={table.numero}")

    return render(request, "riad/commande.html", {
        "table": table,
        "service": service,
        "order": order,
        "menus": menus,
        "add_guest_mode": add_guest_mode,
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

    guest_count = max(int(draft.get("guest_count") or 0), 0)
    order.wizard_draft = draft
    order.guests_count = guest_count
    order.save(update_fields=["wizard_draft", "guests_count", "updated_at"])

    return JsonResponse({"success": True})


@require_POST
def api_update_covers(request, numero):
    table = get_object_or_404(
        DiningTable.objects.select_related("room"),
        numero=numero,
    )
    service = get_or_create_service(table)
    order = DiningOrder.objects.filter(service=service).first()

    if not order:
        return JsonResponse(
            {"success": False, "error": "Aucune commande active."},
            status=404,
        )

    if order_is_locked(order):
        return JsonResponse(
            {"success": False, "error": "Commande déjà réglée."},
            status=403,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "JSON invalide."},
            status=400,
        )

    covers = max(int(payload.get("guests_count", order.guests_count)), 0)
    order.guests_count = covers
    order.save(update_fields=["guests_count", "updated_at"])

    order = load_order_for_details(order)
    prefetch_workflow_items_for_orders(
        [order],
        services_by_order_id={order.id: service},
    )

    return JsonResponse(
        build_table_details(table, service, order)
    )


@require_POST
@transaction.atomic
def api_add_order_guest(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)
    order = get_object_or_404(DiningOrder, service=service)

    if order_is_locked(order):
        return JsonResponse(
            {"success": False, "error": "Commande déjà réglée."},
            status=403,
        )

    if not order.is_sent_to_kitchen:
        return JsonResponse(
            {
                "success": False,
                "error": "La commande doit être envoyée en cuisine avant d'ajouter un client tardif.",
            },
            status=400,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "JSON invalide."},
            status=400,
        )

    guest_data = payload.get("guest")
    if not isinstance(guest_data, dict):
        return JsonResponse(
            {"success": False, "error": "Données client invalides."},
            status=400,
        )

    guest_number = int(guest_data.get("number") or get_next_guest_number(order))
    if order.guests.filter(guest_number=guest_number).exists():
        return JsonResponse(
            {"success": False, "error": "Ce numéro de client existe déjà."},
            status=400,
        )

    guest_data["number"] = guest_number
    guest_order, created_choices = create_guest_from_payload(order, guest_data)
    tickets = send_guest_choices_to_kitchen(
        order,
        table,
        service,
        created_choices,
    )
    sync_service_flags_from_order(service, order)

    return JsonResponse({
        "success": True,
        "guest_number": guest_order.guest_number,
        "tickets_created": len(tickets),
        "total": float(compute_order_total(order)),
    })


@require_POST
@transaction.atomic
def api_delete_order_guest(request, numero):
    table = get_object_or_404(DiningTable, numero=numero)
    service = get_or_create_service(table)
    order = get_object_or_404(DiningOrder, service=service)

    if order_is_locked(order):
        return JsonResponse(
            {"success": False, "error": "Commande déjà réglée."},
            status=403,
        )

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "JSON invalide."},
            status=400,
        )

    guest_number = int(payload.get("guest_number", 0))
    confirmed = bool(payload.get("confirmed"))

    result = delete_or_cancel_guest(order, guest_number, confirmed=confirmed)
    if not result.get("success"):
        status = 409 if result.get("requires_confirmation") else 400
        return JsonResponse(result, status=status)

    sync_service_flags_from_order(service, order)

    return JsonResponse({
        "success": True,
        "total": float(compute_order_total(order)),
    })


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

    order = DiningOrder.objects.filter(service=service).first()
    if order:
        from riad.services.backoffice.archive import mark_order_cancelled

        mark_order_cancelled(order)

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

    if "guests_count" in payload:
        order.guests_count = max(int(payload.get("guests_count") or 0), 0)

    order.save(update_fields=["guests_count", "updated_at"])

    for guest_data in guests:
        create_guest_from_payload(order, guest_data)

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
@transaction.atomic
@log_endpoint_perf("kitchen_toggle")
def api_toggle_kitchen_item(request, item_id):
    item = get_object_or_404(
        KitchenTicketItem.objects.select_related("ticket"),
        id=item_id,
    )

    if item.is_done:
        mark_item_not_ready(item)
    else:
        mark_item_ready(item)

    item.refresh_from_db()
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
@transaction.atomic
def api_mark_all_ticket_items(request, ticket_id):
    data = json.loads(request.body) if request.body else {}
    done = bool(data.get("done", True))

    ticket = get_object_or_404(KitchenTicket, id=ticket_id)
    items = list(ticket.items.all())

    if done:
        for item in items:
            mark_item_ready(item)
    else:
        for item in items:
            mark_item_not_ready(item)

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
    guests_count = max(int(data.get("guests_count", 0)), 0)

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
        create_guest_from_payload(order, guest_data)

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
    service.task_claimed_at = None
    service.task_claimed_extra_ticket = None
    service.task_claimed_by = None
    sync_service_flags_from_order(service, order)
    service.save(
        update_fields=[
            "status",
            "task_claimed_at",
            "task_claimed_extra_ticket",
            "task_claimed_by",
            "updated_at",
        ]
    )

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

    choice.is_cancelled = True
    choice.cancelled_at = timezone.now()
    choice.save(update_fields=["is_cancelled", "cancelled_at"])

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


def build_payment_summary_response(order):
    total = order.total_amount()
    paid = order.paid_amount()
    remaining = order.remaining_amount()
    billing = build_order_billing(order)

    return {
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
                "id": payment.id,
                "method": payment.method,
                "method_display": payment.get_method_display(),
                "amount": float(payment.amount),
                "guest_number": payment.guest_number,
            }
            for payment in order.payments.all()
        ],
        "service_status": order.service.status,
        "internal_tracking": build_internal_payment_tracking(order),
    }


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

    return JsonResponse(build_payment_summary_response(order))


@require_POST
def delete_internal_payment(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("order", "order__service"),
        id=payment_id,
    )
    order = payment.order

    if not order.service_id:
        return JsonResponse(
            {"success": False, "error": "Service introuvable."},
            status=400,
        )

    if order.service.status == "paid":
        return JsonResponse(
            {
                "success": False,
                "error": "Impossible de modifier le suivi interne après encaissement.",
            },
            status=400,
        )

    payment.delete()
    return JsonResponse(build_payment_summary_response(order))