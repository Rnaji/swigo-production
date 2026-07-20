from decimal import Decimal

from riad.models import MenuSectionItem

DRINK_SECTIONS = {"Boisson", "Jus", "Eau"}
MOCKTAIL_CATEGORY = "Mocktail"
COUPE_CATEGORY = "Coupe glacée"
COUPE_PARENT_NAME = "Coupe de glace au choix"

MOCKTAIL_REPLACEMENT_SUPPLEMENT = Decimal("3.50")
COUPE_REPLACEMENT_SUPPLEMENT = Decimal("2.00")


def _menu_section_product_names(menu, section_name):
    return set(
        MenuSectionItem.objects.filter(
            section__menu=menu,
            section__name=section_name,
        ).values_list("product__name", flat=True)
    )


def _menu_has_coupe_choice(menu):
    return MenuSectionItem.objects.filter(
        section__menu=menu,
        section__name="Dessert",
        product__name=COUPE_PARENT_NAME,
    ).exists()


def compute_replacement_supplement(menu, section_name, original_product_name, new_product):
    if not menu or not new_product:
        return Decimal("0.00")

    if original_product_name == new_product.name:
        return Decimal("0.00")

    section_products = _menu_section_product_names(menu, section_name)

    if new_product.name in section_products:
        return Decimal("0.00")

    new_category = new_product.category.name

    if section_name in DRINK_SECTIONS and new_category == MOCKTAIL_CATEGORY:
        return MOCKTAIL_REPLACEMENT_SUPPLEMENT

    if section_name == "Dessert" and new_category == COUPE_CATEGORY:
        if menu.name == "Menu Signature" and _menu_has_coupe_choice(menu):
            return Decimal("0.00")
        return COUPE_REPLACEMENT_SUPPLEMENT

    return Decimal("0.00")
