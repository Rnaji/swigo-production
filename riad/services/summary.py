from collections import defaultdict


SERVICE_SECTION_ORDER = [
    "Mocktail",
    "Boisson",
    "Eau",
    "Entrée",
    "Plat",
    "Dessert",
    "Thé / Café",
]


def build_summary(order, sections=None):
    sections_filter = set(sections) if sections else None
    grouped = defaultdict(lambda: defaultdict(int))

    guests = (
        order.guests
        .prefetch_related(
            "choices__section",
            "choices__product",
        )
        .all()
    )

    for guest in guests:
        for choice in guest.choices.all():
            section_name = choice.section.name
            product_name = choice.product.name

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
            "Dessert",
            "Thé / Café",
        ],
    )