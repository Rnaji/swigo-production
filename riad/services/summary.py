from collections import defaultdict

from riad.services.prefetched_data import (
    PrefetchMissingError,
    get_prefetched_guest_choices,
    get_prefetched_guests,
    get_prefetched_table_extras,
)
from riad.services.pricing import choice_display_name


SERVICE_SECTION_ORDER = [
    "Mocktail",
    "Boisson",
    "Eau",
    "Jus",
    "Entrée",
    "Plat",
    "Dessert",
    "Coupe glacée",
    "Thé / Café",
    "Supplément libre",
]


def choice_summary_section(choice):
    if choice.source == "manual_extra":
        return "Supplément libre"

    if choice.section:
        return choice.section.name

    if choice.product and choice.product.category:
        return choice.product.category.name

    return None


def _iter_billable_choices_from_db(order):
    guests = (
        order.guests
        .select_related("menu")
        .prefetch_related(
            "choices__section",
            "choices__product",
            "choices__product__category",
        )
        .all()
    )

    for guest in guests:
        for choice in guest.choices.all():
            if not choice.is_cancelled:
                yield choice

    for choice in order.table_level_choices.filter(is_cancelled=False).select_related(
        "section",
        "product",
        "product__category",
    ):
        yield choice


def iter_billable_choices(order):
    """
    Itère les choix facturables.
    Chemin optimisé : attributs to_attr (0 SQL).
    Fallback legacy uniquement si l'order n'a pas été préchargé.
    """
    try:
        guests = get_prefetched_guests(order)
        table_extras = get_prefetched_table_extras(order)
    except PrefetchMissingError:
        yield from _iter_billable_choices_from_db(order)
        return

    for guest in guests:
        for choice in get_prefetched_guest_choices(guest):
            if not choice.is_cancelled:
                yield choice

    for choice in table_extras:
        if not choice.is_cancelled:
            yield choice


def build_summary(order, sections=None):
    sections_filter = set(sections) if sections else None
    grouped = defaultdict(lambda: defaultdict(int))

    for choice in iter_billable_choices(order):
        section_name = choice_summary_section(choice)

        if not section_name:
            continue

        if choice.source == "manual_extra":
            product_name = choice.label
        else:
            product_name = choice_display_name(choice)

        if sections_filter and section_name not in sections_filter:
            continue

        grouped[section_name][product_name] += choice.quantity

    result = []

    for section_name in SERVICE_SECTION_ORDER:
        if section_name not in grouped:
            continue

        products = grouped[section_name]

        result.append({
            "section": section_name,
            "items": [
                {
                    "name": product_name,
                    "quantity": quantity,
                }
                for product_name, quantity in products.items()
            ],
        })

    return result


def build_kitchen_summary(order):
    return build_summary(
        order,
        sections=[
            "Entrée",
            "Plat",
        ],
    )


def build_office_summary(order):
    return build_summary(
        order,
        sections=[
            "Mocktail",
            "Boisson",
            "Eau",
            "Jus",
            "Dessert",
            "Coupe glacée",
            "Thé / Café",
            "Supplément libre",
        ],
    )
