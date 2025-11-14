# swigo/templatetags/math_filters.py

from django import template

register = template.Library()

@register.filter
def multiply(quantity, unit_price):
    try:
        return round(float(quantity) * float(unit_price), 2)
    except (ValueError, TypeError):
        return 0

@register.filter
def total_price(articles, args):
    quantity_field, unit_price_field = args.split()
    total = 0
    for article in articles:
        quantity = getattr(article, quantity_field, 0)
        unit_price = getattr(article, unit_price_field, 0)
        try:
            total += float(quantity) * float(unit_price)
        except (ValueError, TypeError):
            continue
    return round(total, 2)
