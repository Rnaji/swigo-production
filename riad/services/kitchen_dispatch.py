from riad.models import KitchenTicket, KitchenTicketItem
from riad.services.kitchen_routing import station_for_manual_extra, station_for_product


def create_kitchen_ticket_item(ticket, item):
    if item.get("label"):
        KitchenTicketItem.objects.create(
            ticket=ticket,
            section=None,
            product=None,
            label=item["label"],
            quantity=item.get("quantity", 1),
            note=item.get("note", ""),
        )
        return

    if not item.get("product"):
        return

    KitchenTicketItem.objects.create(
        ticket=ticket,
        section=item.get("section"),
        product=item["product"],
        quantity=item.get("quantity", 1),
        note=item.get("note", ""),
    )


def send_choice_to_kitchen(order, table, service, choice):
    if choice.source not in ("menu", "extra", "replacement", "manual_extra"):
        return None

    if choice.source == "manual_extra":
        station = station_for_manual_extra(choice.station)
    else:
        station = station_for_product(choice.product)

    ticket = KitchenTicket.objects.create(
        order=order,
        table=table,
        service=service,
        ticket_type="extra",
        station=station,
        course="full",
        status="pending",
    )

    if choice.source == "manual_extra":
        create_kitchen_ticket_item(ticket, {
            "label": choice.label,
            "quantity": choice.quantity,
            "note": choice.note,
        })
    else:
        create_kitchen_ticket_item(ticket, {
            "section": choice.section,
            "product": choice.product,
            "quantity": choice.quantity,
            "note": choice.note,
        })

    return ticket


def build_ticket_items_from_choices(choices):
    product_groups = {}
    manual_items = []

    for choice in choices:
        if choice.source == "manual_extra":
            manual_items.append({
                "station": station_for_manual_extra(choice.station),
                "label": choice.label,
                "quantity": choice.quantity,
                "note": choice.note or "",
            })
            continue

        if choice.source not in ("menu", "replacement", "extra"):
            continue

        if not choice.product:
            continue

        station = station_for_product(choice.product)
        section_name = choice.section.name.strip() if choice.section else ""
        product_name = choice.product.name.strip()

        key = (
            station,
            section_name.lower(),
            product_name.lower(),
            choice.note.strip().lower(),
        )

        if key not in product_groups:
            product_groups[key] = {
                "station": station,
                "section": choice.section,
                "product": choice.product,
                "quantity": 0,
                "note": choice.note,
            }

        product_groups[key]["quantity"] += choice.quantity

    return list(product_groups.values()), manual_items


def group_choices_for_initial_ticket(choices):
    product_items, _manual_items = build_ticket_items_from_choices(choices)
    grouped = {}

    for item in product_items:
        grouped[item["station"], item["product"].id, item["note"]] = item

    return grouped
