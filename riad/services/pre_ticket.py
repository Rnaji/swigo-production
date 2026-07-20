from collections import OrderedDict
from decimal import Decimal

from riad.services.pricing import (
    build_order_billing,
    choice_display_name,
    choice_line_amount,
    compute_order_total,
)
from riad.services.vat import build_vat_summary

DISCLAIMER_LINE = "NE TIENT PAS LIEU DE TICKET DE CAISSE"

RESTAURANT_NAME = "LES 2 PALMIERS"
RESTAURANT_ADDRESS = "112 Rue de la Libération"
RESTAURANT_CITY = "27140 GISORS"


def _format_eur(amount):
    value = float(amount)
    formatted = f"{value:.2f}".replace(".", ",")
    return f"{formatted} €"


class _LineAggregator:
    def __init__(self, use_multiply=False):
        self.use_multiply = use_multiply
        self._groups = OrderedDict()

    def add(self, key, label, amount, quantity=1):
        if key not in self._groups:
            self._groups[key] = {
                "label": label,
                "quantity": 0,
                "amount": Decimal("0"),
            }

        self._groups[key]["quantity"] += quantity
        self._groups[key]["amount"] += Decimal(str(amount))

    def lines(self):
        result = []

        for group in self._groups.values():
            quantity = group["quantity"]
            label = group["label"]

            if self.use_multiply:
                display_label = f"{quantity} × {label}" if quantity > 1 else f"1 × {label}"
            elif quantity > 1:
                display_label = f"{quantity} {label}"
            else:
                display_label = label

            result.append({
                "display_label": display_label,
                "quantity": quantity,
                "label": label,
                "amount": float(group["amount"]),
                "amount_display": _format_eur(group["amount"]),
            })

        return result


def _collect_main_items(guests):
    aggregator = _LineAggregator(use_multiply=True)

    for guest in guests:
        if not guest.menu:
            continue

        menu = guest.menu
        aggregator.add(
            key=f"menu:{menu.name}",
            label=menu.name,
            amount=menu.price,
            quantity=1,
        )

    return aggregator.lines()


def _collect_extras(order, guests):
    aggregator = _LineAggregator(use_multiply=False)

    for guest in guests:
        for choice in guest.choices.all():
            amount = choice_line_amount(choice)
            if amount <= 0:
                continue

            if choice.source not in ("extra", "replacement", "manual_extra"):
                continue

            name = choice_display_name(choice)
            quantity = choice.quantity or 1

            if choice.source == "extra" and choice.product:
                unit_price = choice.product.price
                key = f"extra:{name}:{unit_price}"
            elif choice.source == "manual_extra":
                unit_price = choice.line_total or Decimal("0")
                key = f"manual:{name}:{unit_price}"
            else:
                key = f"replacement:{name}:{amount}"

            aggregator.add(
                key=key,
                label=name,
                amount=amount,
                quantity=quantity,
            )

    for choice in order.table_level_choices.select_related("product").order_by("created_at"):
        amount = choice_line_amount(choice)
        if amount <= 0:
            continue

        name = choice_display_name(choice)
        quantity = choice.quantity or 1

        if choice.product:
            key = f"table-extra:{name}:{choice.product.price}"
        else:
            key = f"table-manual:{name}:{choice.line_total or amount}"

        aggregator.add(
            key=key,
            label=name,
            amount=amount,
            quantity=quantity,
        )

    return aggregator.lines()


def build_pre_ticket(order):
    billing = build_order_billing(order)
    vat_summary = build_vat_summary(order)

    guests = (
        order.guests
        .select_related("menu")
        .prefetch_related("choices__section", "choices__product", "choices__product__category")
        .order_by("guest_number")
    )

    items = _collect_main_items(guests)
    extras = _collect_extras(order, guests)

    vat_rows = []
    for row in vat_summary["rates"]:
        vat_rows.append({
            "rate_display": row["rate_display"],
            "base_ht_display": _format_eur(row["base_ht"]),
            "vat_amount_display": _format_eur(row["vat_amount"]),
            "ttc_display": _format_eur(row["ttc"]),
        })

    grand_total = compute_order_total(order)

    return {
        "restaurant": {
            "name": RESTAURANT_NAME,
            "address": RESTAURANT_ADDRESS,
            "city": RESTAURANT_CITY,
        },
        "table_number": order.service.table.numero,
        "order_id": order.id,
        "generated_at": order.updated_at,
        "disclaimer_line": DISCLAIMER_LINE,
        "items": items,
        "extras": extras,
        "totals": {
            "guests_total": float(billing["guests_total"]),
            "table_extras_total": float(billing["table_extras_total"]),
            "grand_total": float(grand_total),
            "grand_total_display": _format_eur(grand_total),
        },
        "vat_summary": {
            "rates": vat_rows,
            "totals": {
                "base_ht_display": _format_eur(vat_summary["totals"]["base_ht"]),
                "vat_amount_display": _format_eur(vat_summary["totals"]["vat_amount"]),
                "ttc_display": _format_eur(vat_summary["totals"]["ttc"]),
            },
        },
        "billing": billing,
    }
