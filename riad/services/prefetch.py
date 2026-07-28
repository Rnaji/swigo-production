"""
Construction des Prefetch / QuerySet pour les chemins lecture Salle.

Ne contient aucun helper de lecture to_attr (voir prefetched_data.py).
N'importe pas summary, pricing, table_details ni workflow_context.
"""

from django.db.models import Prefetch

from riad.models import (
    DiningOrder,
    GuestChoice,
    GuestOrder,
    KitchenTicketItem,
    Payment,
)

# Aligné sur service_category_readiness.WORKFLOW_TICKET_STATUSES (évite import circulaire).
_WORKFLOW_TICKET_STATUSES = ("pending", "preparing", "ready", "served")


def guest_choices_prefetch():
    return Prefetch(
        "choices",
        queryset=(
            GuestChoice.objects
            .select_related("section", "product", "product__category")
            .order_by("id")
        ),
        to_attr="prefetched_choices",
    )


def guests_prefetch():
    return Prefetch(
        "guests",
        queryset=(
            GuestOrder.objects
            .select_related("menu")
            .prefetch_related(guest_choices_prefetch())
            .order_by("guest_number")
        ),
        to_attr="prefetched_guests",
    )


def table_extras_prefetch():
    return Prefetch(
        "table_level_choices",
        queryset=(
            GuestChoice.objects
            .select_related("section", "product", "product__category")
            .order_by("created_at", "id")
        ),
        to_attr="prefetched_table_extras",
    )


def payments_prefetch():
    return Prefetch(
        "payments",
        queryset=Payment.objects.order_by("id"),
        to_attr="prefetched_payments",
    )


def order_details_prefetch_related():
    return (
        guests_prefetch(),
        table_extras_prefetch(),
        payments_prefetch(),
    )


def orders_queryset_for_details(*, service_ids=None, order_ids=None):
    qs = DiningOrder.objects.select_related("service")
    if service_ids is not None:
        qs = qs.filter(service_id__in=list(service_ids))
    if order_ids is not None:
        qs = qs.filter(id__in=list(order_ids))
    return qs.prefetch_related(*order_details_prefetch_related())


def load_order_for_details(order):
    """Recharge une commande avec tous les prefetch nécessaires, ou la renvoie telle quelle."""
    if order is None:
        return None
    if hasattr(order, "prefetched_guests"):
        return order
    return orders_queryset_for_details(order_ids=[order.id]).first()


def prefetch_workflow_items_for_orders(orders, *, services_by_order_id=None):
    """
    Charge tous les KitchenTicketItem workflow pour plusieurs commandes en une requête.
    Retourne {order_id: [items]} et attache order.prefetched_workflow_items.
    """
    order_list = [order for order in orders if order]
    if not order_list:
        return {}

    order_ids = [order.id for order in order_list]
    queryset = (
        KitchenTicketItem.objects
        .filter(
            ticket__order_id__in=order_ids,
            ticket__status__in=_WORKFLOW_TICKET_STATUSES,
        )
        .select_related(
            "section",
            "product",
            "product__category",
            "ticket",
            "ticket__order",
        )
    )

    if services_by_order_id:
        service_ids = {
            services_by_order_id[order_id].id
            for order_id in order_ids
            if order_id in services_by_order_id
        }
        if service_ids:
            queryset = queryset.filter(ticket__service_id__in=service_ids)

    items_by_order = {order_id: [] for order_id in order_ids}
    for item in queryset:
        items_by_order[item.ticket.order_id].append(item)

    for order in order_list:
        order.prefetched_workflow_items = items_by_order.get(order.id, [])

    return items_by_order


def prefetch_orders_for_table_details(
    *,
    service_ids=None,
    order_ids=None,
    services_by_order_id=None,
):
    """
    Point d'entrée batch : orders + guests/choices/payments + kitchen items.
    """
    orders = list(
        orders_queryset_for_details(service_ids=service_ids, order_ids=order_ids)
    )
    if services_by_order_id is None:
        services_by_order_id = {
            order.id: order.service
            for order in orders
            if getattr(order, "service_id", None)
        }
    prefetch_workflow_items_for_orders(
        orders,
        services_by_order_id=services_by_order_id,
    )
    return orders
