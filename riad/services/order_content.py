from riad.services.summary import iter_billable_choices, choice_summary_section


SERVICE_STEPS = [
    "free",
    "installed",
    "ordering",
    "ordered",
    "drinks_served",
    "starters_served",
    "starters_cleared",
    "mains_served",
    "mains_cleared",
    "desserts_served",
    "desserts_cleared",
    "coffee_served",
    "coffee_cleared",
    "bill_requested",
    "paid",
    "free",
]

DRINK_SECTIONS = frozenset({"Mocktail", "Boisson", "Eau", "Jus"})
STARTER_SECTIONS = frozenset({"Entrée"})
MAIN_SECTIONS = frozenset({"Plat"})
DESSERT_SECTIONS = frozenset({"Dessert", "Coupe glacée"})
COFFEE_SECTIONS = frozenset({"Thé / Café"})

WORKFLOW_PRODUCT_SECTIONS = {
    "ordered": list(DRINK_SECTIONS),
    "drinks_served": list(STARTER_SECTIONS),
    "starters_cleared": list(MAIN_SECTIONS),
    "mains_cleared": list(DESSERT_SECTIONS),
    "desserts_cleared": list(COFFEE_SECTIONS),
}


def _choice_section_name(choice):
    section_name = choice_summary_section(choice)

    if section_name == "Supplément libre":
        return None

    if section_name:
        return section_name

    if choice.product and choice.product.category:
        return choice.product.category.name

    return None


def _order_has_sections(order, sections):
    if not order:
        return False

    target = frozenset(sections)

    for choice in iter_billable_choices(order):
        section_name = _choice_section_name(choice)
        if section_name and section_name in target:
            return True

    return False


def order_has_drinks(order):
    return _order_has_sections(order, DRINK_SECTIONS)


def order_has_starters(order):
    return _order_has_sections(order, STARTER_SECTIONS)


def order_has_mains(order):
    return _order_has_sections(order, MAIN_SECTIONS)


def order_has_desserts(order):
    return _order_has_sections(order, DESSERT_SECTIONS)


def order_has_coffee(order):
    return _order_has_sections(order, COFFEE_SECTIONS)


def get_order_service_flags(order):
    return {
        "has_drinks": order_has_drinks(order),
        "has_starters": order_has_starters(order),
        "has_mains": order_has_mains(order),
        "has_desserts": order_has_desserts(order),
        "has_coffee": order_has_coffee(order),
    }


def optional_step_flags(flags):
    return {
        "drinks_served": flags["has_drinks"],
        "starters_served": flags["has_starters"],
        "starters_cleared": flags["has_mains"],
        "mains_served": flags["has_mains"],
        "mains_cleared": flags["has_mains"],
        "desserts_served": flags["has_desserts"],
        "desserts_cleared": flags["has_coffee"],
        "coffee_served": flags["has_coffee"],
        "coffee_cleared": flags["has_coffee"],
    }


def compute_next_status(current_status, flags):
    optional_steps = optional_step_flags(flags)

    try:
        current_index = SERVICE_STEPS.index(current_status)
    except ValueError:
        return None

    for next_status in SERVICE_STEPS[current_index + 1:]:
        if next_status in optional_steps and not optional_steps[next_status]:
            continue

        return next_status

    return None


def resolve_workflow_status(service, order):
    """
    Retourne le statut dont le workflow doit être affiché,
    en sautant les étapes produits vides pour la commande réelle.
    """
    if not order:
        return service.status

    status = service.status
    flags = get_order_service_flags(order)

    for _ in range(len(SERVICE_STEPS)):
        sections = WORKFLOW_PRODUCT_SECTIONS.get(status)
        if not sections:
            return status

        if _order_has_sections(order, sections):
            return status

        next_status = compute_next_status(status, flags)
        if not next_status or next_status == status:
            return status

        status = next_status

    return status


def sync_service_flags_from_order(service, order):
    flags = get_order_service_flags(order)

    service.has_drinks = flags["has_drinks"]
    service.has_starters = flags["has_starters"]
    service.has_desserts = flags["has_desserts"]
    service.has_coffee = flags["has_coffee"]
    service.save(
        update_fields=[
            "has_drinks",
            "has_starters",
            "has_desserts",
            "has_coffee",
            "updated_at",
        ]
    )

    return flags
