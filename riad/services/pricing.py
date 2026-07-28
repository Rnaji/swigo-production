from decimal import Decimal

from riad.services.prefetched_data import (
    PrefetchMissingError,
    get_prefetched_guest_choices,
    get_prefetched_guests,
    get_prefetched_payments,
    get_prefetched_table_extras,
)


def choice_line_amount(choice):
    if choice.source == "menu":
        return Decimal("0.00")

    if choice.source == "offered":
        return Decimal("0.00")

    if choice.source == "replacement":
        return choice.supplement_amount or Decimal("0.00")

    if choice.source == "manual_extra":
        return choice.line_total or Decimal("0.00")

    if choice.source == "extra":
        if not choice.product:
            return Decimal("0.00")
        return choice.product.price * choice.quantity

    return Decimal("0.00")


def compute_guest_total(guest):
    total = Decimal("0.00")

    if guest.menu:
        total += guest.menu.price

    try:
        choices = get_prefetched_guest_choices(guest)
    except PrefetchMissingError:
        choices = list(guest.choices.select_related("product"))

    for choice in choices:
        total += choice_line_amount(choice)

    return total


def compute_table_extras_total(order):
    total = Decimal("0.00")

    try:
        extras = get_prefetched_table_extras(order)
    except PrefetchMissingError:
        extras = list(order.table_level_choices.select_related("product"))

    for choice in extras:
        total += choice_line_amount(choice)

    return total


def compute_guest_paid_amount(order, guest_number):
    try:
        payments = get_prefetched_payments(order)
    except PrefetchMissingError:
        payments = list(order.payments.filter(guest_number=guest_number))
        return sum((payment.amount for payment in payments), Decimal("0.00"))

    return sum(
        (
            payment.amount
            for payment in payments
            if payment.guest_number == guest_number
        ),
        Decimal("0.00"),
    )


def compute_guest_remaining(guest):
    paid = compute_guest_paid_amount(guest.order, guest.guest_number)
    remaining = compute_guest_total(guest) - paid
    return max(remaining, Decimal("0.00"))


def compute_order_total(order):
    try:
        guests = get_prefetched_guests(order)
    except PrefetchMissingError:
        guests = list(
            order.guests.select_related("menu").prefetch_related("choices__product")
        )

    total = Decimal("0.00")
    for guest in guests:
        total += compute_guest_total(guest)

    total += compute_table_extras_total(order)
    return total


def build_order_billing(order):
    guests_total = Decimal("0.00")
    guest_summaries = []

    try:
        guests = get_prefetched_guests(order)
    except PrefetchMissingError:
        guests = list(
            order.guests
            .select_related("menu")
            .prefetch_related("choices__section", "choices__product")
            .order_by("guest_number")
        )

    for guest in guests:
        guest_total = compute_guest_total(guest)
        guest_paid = compute_guest_paid_amount(order, guest.guest_number)
        guest_remaining = max(guest_total - guest_paid, Decimal("0.00"))

        guests_total += guest_total

        guest_summaries.append({
            "guest_number": guest.guest_number,
            "total": guest_total,
            "paid": guest_paid,
            "remaining": guest_remaining,
            "is_paid": guest_paid >= guest_total,
        })

    table_extras_total = compute_table_extras_total(order)
    order_total = guests_total + table_extras_total

    return {
        "guests": guest_summaries,
        "guests_total": guests_total,
        "table_extras_total": table_extras_total,
        "order_total": order_total,
    }


def choice_display_name(choice):
    if choice.source == "manual_extra":
        return choice.label

    if choice.product:
        return choice.product.name

    return choice.label or ""
