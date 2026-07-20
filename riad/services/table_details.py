from riad.services.pricing import (
    choice_display_name,
    choice_line_amount,
    build_order_billing,
    compute_order_total,
)
from riad.services.summary import (
    build_summary,
    build_kitchen_summary,
    build_office_summary,
)

from riad.services.workflow import get_workflow_step
from riad.services.timeline import build_timeline
from riad.services.order_content import resolve_workflow_status


def build_table_details(table, service, order):
    """
    Construit toutes les informations nécessaires
    à l'affichage d'une table.
    """

    workflow_status = resolve_workflow_status(service, order)
    workflow = get_workflow_step(workflow_status)
    timeline = build_timeline(service)

    data = service.to_dict()

    data["id"] = table.id
    data["numero"] = table.numero
    data["room"] = table.room.name
    data["reservation"] = None

    # =====================================================
    # WORKFLOW
    # =====================================================

    data["workflow"] = workflow
    data["timeline"] = timeline

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

    if service.status == "bill_requested":
        data["next_action"]["title"] = "Présenter le récapitulatif"
        data["next_action"]["button"] = "Voir le pré-ticket"
        data["next_action"]["type"] = "open_pre_ticket"
        data["next_action"]["pre_ticket_url"] = (
            f"/riad/table/{table.id}/pre-ticket/"
        )

    data["action"] = data["next_action"]["title"]
    data["icon"] = workflow.get("icon", data.get("icon"))

    # =====================================================
    # RÉSUMÉS
    # =====================================================

    data["summary"] = []
    data["kitchen_summary"] = []
    data["office_summary"] = []

    # =====================================================
    # COMMANDE / ADDITION
    # =====================================================

    data["order"] = {
        "exists": False,
        "id": None,
        "guests_count": 0,
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

    data["summary"] = build_summary(order)
    data["kitchen_summary"] = build_kitchen_summary(order)
    data["office_summary"] = build_office_summary(order)

    if workflow["type"] == "products":
        data["next_action"]["items"] = build_summary(
            order,
            sections=workflow["sections"],
        )

    # =====================================================
    # ADDITION
    # =====================================================

    total = compute_order_total(order)
    paid = order.paid_amount()
    remaining = order.remaining_amount()
    billing = build_order_billing(order)
    billing_by_guest = {
        item["guest_number"]: item for item in billing["guests"]
    }

    data["order"]["exists"] = True
    data["order"]["id"] = order.id
    data["order"]["guests_count"] = order.guests_count
    data["order"]["guests_total"] = float(billing["guests_total"])
    data["order"]["table_extras_total"] = float(billing["table_extras_total"])
    data["order"]["total"] = float(total)
    data["order"]["paid"] = float(paid)
    data["order"]["remaining"] = float(max(remaining, 0))

    data["order"]["payments"] = [
        {
            "method": payment.method,
            "method_display": payment.get_method_display(),
            "amount": float(payment.amount),
            "guest_number": payment.guest_number,
        }
        for payment in order.payments.all()
    ]

    # =====================================================
    # COMMANDE DÉTAILLÉE
    # =====================================================

    guests = (
        order.guests
        .prefetch_related(
            "choices__section",
            "choices__product",
        )
        .order_by("guest_number")
    )

    for guest in guests:
        guest_billing = billing_by_guest.get(guest.guest_number, {})
        guest_data = {
            "guest_number": guest.guest_number,
            "menu": guest.menu.name if guest.menu else None,
            "menu_price": float(guest.menu.price) if guest.menu else 0,
            "total": float(guest_billing.get("total", 0)),
            "paid": float(guest_billing.get("paid", 0)),
            "remaining": float(guest_billing.get("remaining", 0)),
            "is_paid": guest_billing.get("is_paid", False),
            "choices": [],
        }

        for choice in guest.choices.all():
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

    table_extras = (
        order.table_level_choices
        .select_related("section", "product", "product__category")
        .order_by("created_at")
    )

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