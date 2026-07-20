BAR_CATEGORIES = {
    "mocktail",
    "boisson",
    "eau",
    "jus",
    "dessert",
    "coupe glacée",
    "thé / café",
    "the / cafe",
    "thé",
    "café",
}


def station_for_product(product):
    if not product:
        return "kitchen"

    category_name = product.category.name.strip().lower()
    return "bar" if category_name in BAR_CATEGORIES else "kitchen"


def station_for_manual_extra(station):
    return station if station in ("kitchen", "bar") else "kitchen"
