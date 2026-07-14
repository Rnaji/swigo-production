from riad.services.summary import (
    build_summary,
    build_kitchen_summary,
    build_office_summary,
)

from riad.services.workflow import get_workflow_step
from riad.services.timeline import build_timeline


def build_table_details(table, service, order):
    """
    Construit toutes les informations nécessaires
    à l'affichage d'une table.
    """

    workflow = get_workflow_step(service.status)
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

    total = order.total_amount()
    paid = order.paid_amount()
    remaining = order.remaining_amount()

    data["order"]["exists"] = True
    data["order"]["id"] = order.id
    data["order"]["guests_count"] = order.guests_count
    data["order"]["total"] = float(total)
    data["order"]["paid"] = float(paid)
    data["order"]["remaining"] = float(max(remaining, 0))

    data["order"]["payments"] = [
        {
            "method": payment.method,
            "method_display": payment.get_method_display(),
            "amount": float(payment.amount),
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
        guest_data = {
            "guest_number": guest.guest_number,
            "menu": guest.menu.name if guest.menu else None,
            "menu_price": float(guest.menu.price) if guest.menu else 0,
            "choices": [],
        }

        for choice in guest.choices.all():
            guest_data["choices"].append({
                "section": choice.section.name if choice.section else "",
                "product": choice.product.name,
                "quantity": choice.quantity,
                "source": choice.source,
                "price": float(choice.product.price),
                "line_total": float(choice.product.price * choice.quantity),
            })

        data["order"]["guests"].append(guest_data)

    return data