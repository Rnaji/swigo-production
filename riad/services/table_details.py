from riad.services.pricing import (
    choice_display_name,
    choice_line_amount,
    build_order_billing,
    compute_order_total,
)
from riad.services.prefetched_data import (
    get_prefetched_guest_choices,
    get_prefetched_guests,
    get_prefetched_payments,
    get_prefetched_table_extras,
    get_prefetched_workflow_items,
)
from riad.services.summary import (
    build_summary,
    build_kitchen_summary,
    build_office_summary,
)

from riad.services.workflow import get_workflow_step
from riad.services.timeline import build_timeline
from riad.services.order_content import resolve_workflow_status
from riad.services.workflow_engine import get_service_workflow_snapshot


def build_table_details(
    table,
    service,
    order,
    *,
    workflow_snapshot=None,
    prefetched_items=None,
):
    """
    Construit le JSON d'affichage d'une table.

    Fonction pure côté SQL : aucune requête. L'appelant doit avoir préchargé
    order (guests/menu/choices/payments/table extras) et les kitchen items
    via riad.services.prefetch.
    """

    if prefetched_items is None and order is not None:
        prefetched_items = get_prefetched_workflow_items(order)

    if workflow_snapshot is None:
        workflow_snapshot = get_service_workflow_snapshot(
            service,
            order,
            context="salle",
            prefetched_items=prefetched_items,
        )

    read_ctx = workflow_snapshot.get("_ctx")
    if read_ctx:
        workflow_status = read_ctx.get_workflow_status()
    else:
        workflow_status = resolve_workflow_status(service, order)

    workflow = get_workflow_step(workflow_status)
    timeline = build_timeline(service, order, workflow_snapshot=workflow_snapshot)
    category_action = workflow_snapshot.get("table_action")

    data = service.to_dict()

    data["id"] = table.id
    data["numero"] = table.numero
    data["room"] = table.room.name

    data["workflow"] = workflow
    data["timeline"] = timeline
    data["workflow_snapshot"] = {
        "active_category": workflow_snapshot.get("active_category"),
        "phase": workflow_snapshot.get("phase"),
        "category_phases": workflow_snapshot.get("category_phases"),
    }

    data["next_action"] = {
        "title": workflow["title"],
        "button": workflow["button"],
        "type": workflow["type"],
        "sections": workflow["sections"],
        "items": [],
    }

    if service.status == "ordering":
        has_draft = bool(order and order.has_wizard_draft)
        data["next_action"]["title"] = "Finaliser la commande"
        data["next_action"]["button"] = (
            "Reprendre la commande" if has_draft else "Continuer la commande"
        )
        data["next_action"]["type"] = "open_commande"
        data["next_action"]["has_wizard_draft"] = has_draft

    if category_action:
        data["next_action"].update(category_action)
        if category_action.get("type") == "products" and order:
            data["next_action"]["items"] = build_summary(
                order,
                sections=category_action.get("sections") or [],
            )

    if service.status == "bill_requested":
        data["next_action"]["title"] = "Paiement"
        data["next_action"]["button"] = ""
        data["next_action"]["type"] = "payment"
        data["next_action"].pop("pre_ticket_url", None)
        data["next_action"].pop("sections", None)
        data["next_action"]["items"] = []

    # Carte Salle : afficher « X servis depuis… » ; le drawer garde le titre Débarrasser.
    if category_action and category_action.get("served_since_label"):
        data["action"] = category_action["served_since_label"]
    else:
        data["action"] = data["next_action"]["title"]
    data["icon"] = workflow.get("icon", data.get("icon"))

    data["summary"] = []
    data["kitchen_summary"] = []
    data["office_summary"] = []

    data["order"] = {
        "exists": False,
        "id": None,
        "guests_count": 0,
        "clients_count": 0,
        "guests": [],
        "table_extras": [],
        "guests_total": 0,
        "table_extras_total": 0,
        "total": 0,
        "paid": 0,
        "remaining": 0,
        "payments": [],
    }

    if not order:
        return data

    # Accès stricts : PrefetchMissingError si non préchargé (jamais de SQL ici).
    guests = get_prefetched_guests(order)
    payments = get_prefetched_payments(order)
    table_extras = get_prefetched_table_extras(order)

    data["summary"] = build_summary(order)
    data["kitchen_summary"] = build_kitchen_summary(order)
    data["office_summary"] = build_office_summary(order)

    if workflow["type"] == "products" and not category_action:
        data["next_action"]["items"] = build_summary(
            order,
            sections=workflow["sections"],
        )

    total = compute_order_total(order)
    paid = order.paid_amount()
    remaining = total - paid
    billing = build_order_billing(order)
    billing_by_guest = {
        item["guest_number"]: item for item in billing["guests"]
    }

    data["order"]["exists"] = True
    data["order"]["id"] = order.id
    data["order"]["guests_count"] = order.guests_count
    data["order"]["clients_count"] = len(guests)
    data["order"]["is_sent_to_kitchen"] = order.is_sent_to_kitchen
    data["order"]["guests_total"] = float(billing["guests_total"])
    data["order"]["table_extras_total"] = float(billing["table_extras_total"])
    data["order"]["total"] = float(total)
    data["order"]["paid"] = float(paid)
    data["order"]["remaining"] = float(max(remaining, 0))

    data["order"]["payments"] = [
        {
            "id": payment.id,
            "method": payment.method,
            "method_display": payment.get_method_display(),
            "amount": float(payment.amount),
            "guest_number": payment.guest_number,
        }
        for payment in payments
    ]

    for guest in guests:
        guest_billing = billing_by_guest.get(guest.guest_number, {})
        guest_data = {
            "guest_number": guest.guest_number,
            "menu": guest.menu.name if guest.menu else None,
            "menu_price": float(guest.menu.price if guest.menu else 0),
            "total": float(guest_billing.get("total", 0)),
            "paid": float(guest_billing.get("paid", 0)),
            "remaining": float(guest_billing.get("remaining", 0)),
            "is_paid": guest_billing.get("is_paid", False),
            "choices": [],
        }

        for choice in get_prefetched_guest_choices(guest):
            guest_data["choices"].append({
                "id": choice.id,
                "section": choice.section.name if choice.section else "",
                "product": choice_display_name(choice),
                "quantity": choice.quantity,
                "source": choice.source,
                "supplement_amount": float(choice.supplement_amount),
                "line_total": float(choice.line_total) if choice.line_total is not None else None,
                "replaced_product_name": choice.replaced_product_name,
                "price": float(choice.product.price) if choice.product else 0,
                "line_amount": float(choice_line_amount(choice)),
            })

        data["order"]["guests"].append(guest_data)

    for choice in table_extras:
        data["order"]["table_extras"].append({
            "id": choice.id,
            "section": choice.section.name if choice.section else "",
            "product": choice_display_name(choice),
            "quantity": choice.quantity,
            "source": choice.source,
            "supplement_amount": float(choice.supplement_amount),
            "line_total": float(choice.line_total) if choice.line_total is not None else None,
            "replaced_product_name": choice.replaced_product_name,
            "price": float(choice.product.price) if choice.product else 0,
            "line_amount": float(choice_line_amount(choice)),
            "scope": "table",
        })

    return data
