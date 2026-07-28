import uuid
from collections import defaultdict

from django.db import transaction
from django.utils import timezone

from riad.models import KitchenTicket, KitchenTicketItem
from riad.services.service_category_readiness import (
    CATEGORY_SECTIONS,
    WORKFLOW_TICKET_STATUSES,
    SERVICE_STEPS,
    get_category_workflow_items,
    infer_ticket_category,
    is_category_fully_served,
    kitchen_item_belongs_to_category,
    kitchen_item_section_name,
    log_serve_action_state,
    should_show_category_serve_task,
)
from riad.services.workflow_engine import advance_service_status_from_line_state

CATEGORY_SERVE_TITLES = {
    "mains": "Servir les plats",
    "desserts": "Servir les desserts",
    "starters": "Servir les entrées",
    "drinks": "Servir les boissons",
    "coffee": "Servir le thé / café",
}

SERVER_HIDDEN_NOTES = frozenset({
    "supplément",
})

CATEGORY_SERVE_PHASE_STATUS = {
    "drinks": "ordered",
    "starters": "drinks_served",
    "mains": "starters_cleared",
    "desserts": "mains_cleared",
    "coffee": "desserts_cleared",
}

TASK_KEY_AVAILABLE_PREFIX = "serve:available:"
TASK_KEY_BATCH_PREFIX = "serve:batch:"
TASK_KEY_EXTRA_AVAILABLE_PREFIX = "serve:extra:available:"
TASK_KEY_EXTRA_BATCH_PREFIX = "serve:extra:batch:"


def _status_index(status):
    try:
        return SERVICE_STEPS.index(status)
    except ValueError:
        return -1


def item_display_label(item):
    if item.label:
        return item.label
    if item.product_id and item.product:
        return item.product.name
    return "Article"


def get_server_visible_note(item):
    note = (item.note or "").strip()
    if not note:
        return ""
    if note.lower() in SERVER_HIDDEN_NOTES:
        return ""
    return note


def aggregate_item_lines(items):
    grouped = {}

    for item in items:
        name = item_display_label(item)
        note = get_server_visible_note(item)
        key = (name.lower(), note.lower())

        if key not in grouped:
            grouped[key] = {
                "name": name,
                "quantity": 0,
                "note": note,
            }

        grouped[key]["quantity"] += item.quantity

    return list(grouped.values())


def infer_item_category(item):
    for category in CATEGORY_SECTIONS:
        if kitchen_item_belongs_to_category(item, category):
            return category
    return None


def get_active_serve_items_for_service(service):
    if not service:
        return KitchenTicketItem.objects.none()

    # KitchenTicket.status="served" = bon clôturé en Cuisine/Office (pas servi en salle).
    # KitchenTicketItem.is_served = article réellement servé au client.
    return (
        KitchenTicketItem.objects
        .filter(
            ticket__service=service,
            ticket__status__in=WORKFLOW_TICKET_STATUSES,
            is_done=True,
            is_served=False,
        )
        .select_related(
            "ticket",
            "section",
            "product",
            "product__category",
            "serve_claimed_by",
        )
        .order_by("done_at", "id")
    )


def category_has_blocking_items(order, category, service=None):
    items = get_category_workflow_items(order, category, service=service)
    return any(not item.is_served for item in items)


def category_all_active_items_served(order, category, service=None):
    if service is None:
        items = get_category_workflow_items(order, category)
        if not items:
            return False
        return all(item.is_served for item in items)

    return is_category_fully_served(service, order, category)


def maybe_advance_service_after_category_served(service, order, category):
    if not order:
        return False
    return advance_service_status_from_line_state(
        service,
        order,
        source=f"serve:{category}",
    )


def mark_all_ready_category_items_served(service, category, now):
    items = list(
        KitchenTicketItem.objects
        .filter(
            ticket__service=service,
            ticket__status__in=WORKFLOW_TICKET_STATUSES,
            is_done=True,
            is_served=False,
        )
        .select_related("ticket", "section", "product", "product__category")
    )
    category_items = [
        item for item in items
        if kitchen_item_belongs_to_category(item, category)
    ]
    if not category_items:
        return []

    KitchenTicketItem.objects.filter(
        id__in=[item.id for item in category_items]
    ).update(
        is_served=True,
        served_at=now,
        serve_batch_id=None,
        serve_claimed_by_id=None,
        serve_claimed_at=None,
    )

    return category_items


def clear_item_serve_state(item, *, clear_done=False):
    update_fields = []

    if clear_done:
        item.is_done = False
        item.done_at = None
        update_fields.extend(["is_done", "done_at"])

    if not item.is_served:
        item.serve_batch_id = None
        item.serve_claimed_by = None
        item.serve_claimed_at = None
        update_fields.extend(["serve_batch_id", "serve_claimed_by", "serve_claimed_at"])

    if update_fields:
        item.save(update_fields=update_fields)


def mark_item_ready(item, ready_at=None):
    item.is_done = True
    item.done_at = ready_at or timezone.now()
    item.save(update_fields=["is_done", "done_at"])


def mark_item_not_ready(item):
    clear_item_serve_state(item, clear_done=True)


def _group_available_items(items):
    main_groups = defaultdict(list)
    extra_groups = defaultdict(list)

    for item in items:
        if item.serve_batch_id:
            continue

        if item.ticket.ticket_type == "extra":
            extra_groups[item.ticket_id].append(item)
            continue

        category = infer_item_category(item)
        if category:
            main_groups[category].append(item)

    return main_groups, extra_groups


def _group_claimed_items(items):
    batches = defaultdict(list)

    for item in items:
        if item.serve_batch_id:
            batches[item.serve_batch_id].append(item)

    return batches


def available_task_key(category):
    return f"{TASK_KEY_AVAILABLE_PREFIX}{category}"


def batch_task_key(batch_id):
    return f"{TASK_KEY_BATCH_PREFIX}{batch_id}"


def extra_available_task_key(ticket_id):
    return f"{TASK_KEY_EXTRA_AVAILABLE_PREFIX}{ticket_id}"


def extra_batch_task_key(batch_id):
    return f"{TASK_KEY_EXTRA_BATCH_PREFIX}{batch_id}"


def parse_serve_task_key(task_key):
    if task_key.startswith(TASK_KEY_AVAILABLE_PREFIX):
        return {
            "kind": "available",
            "category": task_key[len(TASK_KEY_AVAILABLE_PREFIX):],
        }
    if task_key.startswith(TASK_KEY_BATCH_PREFIX):
        return {
            "kind": "batch",
            "batch_id": uuid.UUID(task_key[len(TASK_KEY_BATCH_PREFIX):]),
        }
    if task_key.startswith(TASK_KEY_EXTRA_AVAILABLE_PREFIX):
        return {
            "kind": "extra_available",
            "ticket_id": int(task_key[len(TASK_KEY_EXTRA_AVAILABLE_PREFIX):]),
        }
    if task_key.startswith(TASK_KEY_EXTRA_BATCH_PREFIX):
        return {
            "kind": "extra_batch",
            "batch_id": uuid.UUID(task_key[len(TASK_KEY_EXTRA_BATCH_PREFIX):]),
        }
    return None


def is_serve_task_key(task_key):
    return bool(task_key and task_key.startswith("serve:"))


def _ready_at_for_items(items):
    done_times = [item.done_at for item in items if item.done_at]
    if done_times:
        return min(done_times)
    return timezone.now()


def _serialize_serve_task(
    service,
    *,
    task_key,
    title,
    items,
    serve_category=None,
    extra_ticket_id=None,
    current_user=None,
):
    ready_at = _ready_at_for_items(items)
    claimed = bool(items and items[0].serve_batch_id)
    claimed_by_id = items[0].serve_claimed_by_id if items else None
    claimed_by_me = False

    if claimed and current_user and current_user.is_authenticated:
        claimed_by_me = claimed_by_id == current_user.id
    elif claimed and (not current_user or not current_user.is_authenticated):
        claimed_by_me = True

    task_items = aggregate_item_lines(items)

    return {
        "task_key": task_key,
        "title": title,
        "label": title,
        "lines": task_items,
        "items": task_items,
        "item_ids": [item.id for item in items],
        "serve_category": serve_category,
        "extra_ticket_id": extra_ticket_id,
        "ready_at": ready_at,
        "claimed": claimed,
        "claimed_by_me": claimed_by_me,
        "claimed_by_id": claimed_by_id,
        "service_id": service.id,
    }


def build_serve_tasks_for_service(service, order=None, current_user=None, *, workflow_snapshot=None):
    items = list(get_active_serve_items_for_service(service))
    tasks = []

    serve_flags = (
        (workflow_snapshot or {}).get("should_show_serve_task")
        if workflow_snapshot
        else None
    )

    def _should_show_serve(category):
        if serve_flags is not None:
            return serve_flags.get(category, False)
        if order:
            return should_show_category_serve_task(service, order, category)
        return False

    main_available, extra_available = _group_available_items(items)
    claimed_batches = _group_claimed_items(items)

    for category, group_items in main_available.items():
        if not group_items:
            continue
        if order and not _should_show_serve(category):
            continue
        tasks.append(
            _serialize_serve_task(
                service,
                task_key=available_task_key(category),
                title=CATEGORY_SERVE_TITLES.get(category, "Servir"),
                items=group_items,
                serve_category=category,
                current_user=current_user,
            )
        )

    for ticket_id, group_items in extra_available.items():
        tasks.append(
            _serialize_serve_task(
                service,
                task_key=extra_available_task_key(ticket_id),
                title="Servir un extra",
                items=group_items,
                serve_category=infer_item_category(group_items[0]),
                extra_ticket_id=ticket_id,
                current_user=current_user,
            )
        )

    for batch_id, group_items in claimed_batches.items():
        if not group_items:
            continue

        first = group_items[0]
        category = infer_item_category(first)
        if first.ticket.ticket_type == "extra":
            task_key = extra_batch_task_key(batch_id)
            title = "Servir un extra"
            extra_ticket_id = first.ticket_id
        else:
            task_key = batch_task_key(batch_id)
            title = CATEGORY_SERVE_TITLES.get(category, "Servir")
            extra_ticket_id = None

        if order and category and not _should_show_serve(category):
            continue

        tasks.append(
            _serialize_serve_task(
                service,
                task_key=task_key,
                title=title,
                items=group_items,
                serve_category=infer_item_category(first),
                extra_ticket_id=extra_ticket_id,
                current_user=current_user,
            )
        )

    return tasks


def _items_for_available_task(service, parsed):
    qs = (
        KitchenTicketItem.objects
        .select_for_update()
        .filter(
            ticket__service=service,
            ticket__status__in=WORKFLOW_TICKET_STATUSES,
            is_done=True,
            is_served=False,
            serve_batch_id__isnull=True,
        )
        .select_related("ticket", "section", "product", "product__category")
        .order_by("done_at", "id")
    )

    if parsed["kind"] == "available":
        return [
            item for item in qs
            if item.ticket.ticket_type != "extra"
            and infer_item_category(item) == parsed["category"]
        ]

    if parsed["kind"] == "extra_available":
        return list(qs.filter(ticket_id=parsed["ticket_id"], ticket__ticket_type="extra"))

    return []


@transaction.atomic
def claim_serve_task(service, task_key, user):
    parsed = parse_serve_task_key(task_key)
    if not parsed or parsed["kind"] not in {"available", "extra_available"}:
        return None, "Tâche de service invalide."

    items = _items_for_available_task(service, parsed)
    if not items:
        return None, "Cette tâche n'est plus disponible."

    batch_id = uuid.uuid4()
    now = timezone.now()
    user_id = user.id if user and user.is_authenticated else None

    KitchenTicketItem.objects.filter(
        id__in=[item.id for item in items]
    ).update(
        serve_batch_id=batch_id,
        serve_claimed_by_id=user_id,
        serve_claimed_at=now,
    )

    refreshed = list(
        KitchenTicketItem.objects.filter(id__in=[item.id for item in items])
    )

    if parsed["kind"] == "extra_available":
        serialized = _serialize_serve_task(
            service,
            task_key=extra_batch_task_key(batch_id),
            title="Servir un extra",
            items=refreshed,
            serve_category=infer_item_category(refreshed[0]),
            extra_ticket_id=parsed["ticket_id"],
            current_user=user,
        )
    else:
        serialized = _serialize_serve_task(
            service,
            task_key=batch_task_key(batch_id),
            title=CATEGORY_SERVE_TITLES.get(parsed["category"], "Servir"),
            items=refreshed,
            serve_category=parsed["category"],
            current_user=user,
        )

    return serialized, None


@transaction.atomic
def release_serve_task(service, task_key, user):
    parsed = parse_serve_task_key(task_key)
    if not parsed or parsed["kind"] not in {"batch", "extra_batch"}:
        return False, "Tâche de service invalide."

    items = (
        KitchenTicketItem.objects
        .select_for_update()
        .filter(
            ticket__service=service,
            serve_batch_id=parsed["batch_id"],
            is_served=False,
        )
    )

    if not items.exists():
        return False, "Cette tâche n'est plus active."

    if user and user.is_authenticated:
        if items.exclude(serve_claimed_by_id=user.id).exists():
            return False, "Cette tâche est prise par un autre serveur."

    items.update(
        serve_batch_id=None,
        serve_claimed_by_id=None,
        serve_claimed_at=None,
    )
    return True, None


@transaction.atomic
def complete_serve_task(service, order, task_key, user):
    parsed = parse_serve_task_key(task_key)
    if not parsed or parsed["kind"] not in {"batch", "extra_batch"}:
        return False, "Tâche de service invalide."

    items = list(
        KitchenTicketItem.objects
        .select_for_update()
        .filter(
            ticket__service=service,
            serve_batch_id=parsed["batch_id"],
            is_served=False,
        )
        .select_related("ticket", "section", "product", "product__category")
    )

    if not items:
        return False, "Cette tâche n'est plus active."

    if user and user.is_authenticated:
        if any(item.serve_claimed_by_id != user.id for item in items):
            return False, "Cette tâche est prise par un autre serveur."

    batch_categories = {
        category
        for category in (infer_item_category(item) for item in items)
        if category
    }
    for category in sorted(batch_categories):
        if order:
            log_serve_action_state(service, order, category, "BEFORE")

    now = timezone.now()
    KitchenTicketItem.objects.filter(
        id__in=[item.id for item in items]
    ).update(
        is_served=True,
        served_at=now,
        serve_batch_id=None,
        serve_claimed_by_id=None,
        serve_claimed_at=None,
    )

    affected_categories = set()
    affected_tickets = set()

    for item in items:
        affected_tickets.add(item.ticket_id)
        category = infer_item_category(item)
        if category:
            affected_categories.add(category)

    for category in affected_categories:
        extra_items = mark_all_ready_category_items_served(service, category, now)
        for item in extra_items:
            affected_tickets.add(item.ticket_id)

    for ticket_id in affected_tickets:
        ticket_items = list(
            KitchenTicketItem.objects.filter(ticket_id=ticket_id)
        )
        if ticket_items and all(item.is_served for item in ticket_items):
            ticket = KitchenTicket.objects.get(id=ticket_id)
            ticket.status = "served"
            ticket.finished_at = now
            ticket.save(update_fields=["status", "finished_at"])

    if order:
        advance_service_status_from_line_state(
            service,
            order,
            source="complete_serve_task",
        )
        for category in sorted(affected_categories):
            log_serve_action_state(service, order, category, "AFTER")

    return True, None


def filter_serve_tasks_for_user(tasks, user):
    filtered = []

    for task in tasks:
        if task.get("claimed") and not task.get("claimed_by_me"):
            if user and user.is_authenticated and task.get("claimed_by_id"):
                continue
        filtered.append(task)

    return filtered
