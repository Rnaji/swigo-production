from decimal import Decimal, ROUND_HALF_UP

from riad.services.pricing import choice_line_amount

VAT_RATE_REDUCED = Decimal("5.50")
VAT_RATE_STANDARD = Decimal("10.00")
MENU_VAT_RATE = Decimal("10.00")

ALLOWED_VAT_RATES = frozenset({VAT_RATE_REDUCED, VAT_RATE_STANDARD})


def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def parse_vat_rate(value, default=MENU_VAT_RATE):
    if value is None or value == "":
        return default

    rate = Decimal(str(value).replace(",", "."))
    if rate not in ALLOWED_VAT_RATES:
        raise ValueError(f"Taux de TVA invalide : {value}")

    return rate


def split_ttc_to_ht_vat(ttc, vat_rate):
    ttc = money(Decimal(str(ttc)))
    rate_factor = vat_rate / Decimal("100.00")
    base_ht = money(ttc / (Decimal("1.00") + rate_factor))
    vat_amount = money(ttc - base_ht)
    return base_ht, vat_amount


def product_vat_rate(product):
    if not product:
        return MENU_VAT_RATE

    return product.vat_rate


def collect_order_vat_lines(order):
    lines = []

    guests = (
        order.guests
        .select_related("menu")
        .prefetch_related("choices__product")
        .order_by("guest_number")
    )

    for guest in guests:
        if guest.menu:
            menu_rate = guest.menu_applied_vat_rate or MENU_VAT_RATE
            lines.append({
                "label": guest.menu.name,
                "ttc": guest.menu.price,
                "vat_rate": menu_rate,
                "line_type": "menu",
            })

        for choice in guest.choices.all():
            amount = choice_line_amount(choice)
            if amount <= 0:
                continue

            vat_rate = choice.applied_vat_rate
            if vat_rate is None and choice.product_id:
                vat_rate = choice.product.vat_rate
            if vat_rate is None:
                vat_rate = MENU_VAT_RATE

            lines.append({
                "label": _choice_vat_label(choice),
                "ttc": amount,
                "vat_rate": vat_rate,
                "line_type": choice.source,
            })

    table_choices = (
        order.table_level_choices
        .select_related("product")
        .order_by("created_at")
    )

    for choice in table_choices:
        amount = choice_line_amount(choice)
        if amount <= 0:
            continue

        vat_rate = choice.applied_vat_rate
        if vat_rate is None and choice.product_id:
            vat_rate = choice.product.vat_rate
        if vat_rate is None:
            vat_rate = MENU_VAT_RATE

        lines.append({
            "label": _choice_vat_label(choice),
            "ttc": amount,
            "vat_rate": vat_rate,
            "line_type": choice.source,
        })

    return lines


def _choice_vat_label(choice):
    from riad.services.pricing import choice_display_name

    if choice.source == "manual_extra":
        return choice.label

    if choice.source == "replacement":
        return f"Remplacement par {choice_display_name(choice)}"

    if choice.source == "extra" and choice.quantity > 1:
        return f"{choice.quantity} × {choice_display_name(choice)}"

    return choice_display_name(choice)


def build_vat_summary(order):
    lines = collect_order_vat_lines(order)
    groups = {}

    for line in lines:
        rate = line["vat_rate"]
        ttc = money(line["ttc"])
        base_ht, vat_amount = split_ttc_to_ht_vat(ttc, rate)

        if rate not in groups:
            groups[rate] = {
                "rate": rate,
                "rate_label": _rate_label(rate),
                "ttc": Decimal("0.00"),
                "base_ht": Decimal("0.00"),
                "vat_amount": Decimal("0.00"),
                "lines": [],
            }

        groups[rate]["ttc"] += ttc
        groups[rate]["base_ht"] += base_ht
        groups[rate]["vat_amount"] += vat_amount
        groups[rate]["lines"].append({
            "label": line["label"],
            "ttc": float(ttc),
        })

    sorted_rates = sorted(groups.keys())
    rate_rows = []

    totals = {
        "ttc": Decimal("0.00"),
        "base_ht": Decimal("0.00"),
        "vat_amount": Decimal("0.00"),
    }

    for rate in sorted_rates:
        group = groups[rate]
        group["ttc"] = money(group["ttc"])
        group["base_ht"] = money(group["base_ht"])
        group["vat_amount"] = money(group["vat_amount"])

        totals["ttc"] += group["ttc"]
        totals["base_ht"] += group["base_ht"]
        totals["vat_amount"] += group["vat_amount"]

        rate_rows.append({
            "rate": float(rate),
            "rate_label": group["rate_label"],
            "rate_display": _rate_display(rate),
            "ttc": float(group["ttc"]),
            "base_ht": float(group["base_ht"]),
            "vat_amount": float(group["vat_amount"]),
            "lines": group["lines"],
        })

    return {
        "rates": rate_rows,
        "totals": {
            "ttc": float(money(totals["ttc"])),
            "base_ht": float(money(totals["base_ht"])),
            "vat_amount": float(money(totals["vat_amount"])),
        },
    }


def _rate_label(rate):
    if rate == VAT_RATE_REDUCED:
        return "TVA 5,5 %"
    return "TVA 10 %"


def _rate_display(rate):
    if rate == VAT_RATE_REDUCED:
        return "5,5 %"
    return "10 %"
