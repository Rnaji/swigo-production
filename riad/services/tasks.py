from django.utils import timezone

from riad.services.order_content import resolve_workflow_status
from riad.services.serve_tasks import (
    build_serve_tasks_for_service,
    filter_serve_tasks_for_user,
    is_serve_task_key,
)
from riad.services.service_category_readiness import (
    is_clear_task_allowed,
)
from riad.services.workflow_engine import get_service_workflow_snapshot
from riad.services.table_details import build_table_details
from riad.services.workflow import get_workflow_step

INACTIVE_STATUSES = frozenset({"free", "reserved"})

# Plus de file d'attente post-repas : "Apporter l'addition" est une vraie tâche
# à coffee_cleared, validée via /next/ vers bill_requested (paiement).
POST_MEAL_WAITING_STATUSES = frozenset()

OVERDUE_MINUTES = 5

SERVE_CATEGORY_PRIORITY = {
    "mains": 10,
    "desserts": 20,
    "starters": 30,
    "drinks": 40,
    "coffee": 50,
}

PRIORITY_ORDER = 100
PRIORITY_INSTALL = 95
PRIORITY_BILL = 200
PRIORITY_CLEAR = 300
PRIORITY_FREE = 400
PRIORITY_OTHER = 500
PRIORITY_SERVE_EXTRA = 55

CLEARING_SERVED_PREFIXES = {
    "starters_served": "Entrées servies",
    "mains_served": "Plats servis",
    "desserts_served": "Desserts servis",
    "coffee_served": "Thés / cafés servis",
}

TASK_EMOJI = {
    "table_restaurant": "🪑",
    "edit_note": "📝",
    "local_bar": "🥤",
    "restaurant_menu": "🥗",
    "restaurant": "🍽",
    "icecream": "🍰",
    "local_cafe": "☕",
    "cleaning_services": "🧹",
    "receipt_long": "🧾",
    "payments": "💳",
    "check_circle": "✅",
    "arrow_forward": "➡️",
}


def format_elapsed_since(elapsed_seconds):
    minutes = max(int(elapsed_seconds) // 60, 0)

    if minutes <= 0:
        return None

    if minutes == 1:
        return "Depuis 1 min"

    return f"Depuis {minutes} min"


def format_served_since_label(prefix, elapsed_seconds):
    from riad.services.service_category_readiness import (
        format_served_since_label as _format_served_since_label,
    )

    return _format_served_since_label(prefix, elapsed_seconds)


def format_installed_since_label(elapsed_seconds):
    minutes = max(int(elapsed_seconds) // 60, 0)

    if minutes < 1:
        return "👥 Clients installés à l'instant"

    if minutes < 60:
        if minutes == 1:
            return "👥 Clients installés depuis 1 min"
        return f"👥 Clients installés depuis {minutes} min"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"👥 Clients installés depuis {hours} h {remaining_minutes:02d}"


def is_take_order_task(title, service):
    return (
        service.status == "installed"
        and (title or "").strip().lower() == "prendre la commande"
    )


def get_clearing_served_prefix(service, title):
    if "débarrasser" not in (title or "").lower():
        return None

    return CLEARING_SERVED_PREFIXES.get(service.status)


def format_ready_since(ready_at):
    if not ready_at:
        return None

    elapsed = max(int((timezone.now() - ready_at).total_seconds()), 0)
    minutes = elapsed // 60
    seconds = elapsed % 60
    return f"Prêt depuis {minutes:02d}:{seconds:02d}"


def get_task_priority_score(
    *,
    service,
    order,
    title,
    action_type,
    serve_category=None,
):
    if action_type == "serve_items":
        if serve_category:
            return SERVE_CATEGORY_PRIORITY.get(serve_category, PRIORITY_SERVE_EXTRA)
        return PRIORITY_SERVE_EXTRA

    if order:
        workflow_status = resolve_workflow_status(service, order)
    else:
        workflow_status = service.status

    workflow = get_workflow_step(workflow_status)
    title_lower = (title or "").lower()

    if service.status in ("installed", "ordering") or "commande" in title_lower:
        return PRIORITY_ORDER

    if service.status == "installed" or "installer" in title_lower:
        return PRIORITY_INSTALL

    if (
        service.status == "bill_requested"
        or "addition" in title_lower
        or "récapitulatif" in title_lower
        or "encaiss" in title_lower
    ):
        return PRIORITY_BILL

    if workflow.get("icon") == "cleaning_services" or "débarrasser" in title_lower:
        return PRIORITY_CLEAR

    if service.status == "paid" or "libérer" in title_lower:
        return PRIORITY_FREE

    return PRIORITY_OTHER


def task_sort_key(task):
    claimed_by_me_rank = 0 if task.get("claimed_by_me") else 1
    return (
        claimed_by_me_rank,
        task.get("priority_score", PRIORITY_OTHER),
        task.get("sort_timestamp", 0),
    )


def get_task_emoji(icon, title="", action_type=None, serve_category=None):
    if action_type == "serve_items":
        if serve_category == "drinks":
            return "🥤"
        if serve_category == "starters":
            return "🥗"
        if serve_category == "mains":
            return "🍽"
        if serve_category == "desserts":
            return "🍰"
        if serve_category == "coffee":
            return "☕"
        if "extra" in (title or "").lower():
            return "➕"

    if icon in TASK_EMOJI:
        return TASK_EMOJI[icon]

    title_lower = (title or "").lower()

    if "boisson" in title_lower or "mocktail" in title_lower:
        return "🥤"
    if "entrée" in title_lower:
        return "🥗"
    if "plat" in title_lower:
        return "🍽"
    if "dessert" in title_lower or "extra" in title_lower:
        return "🍰"
    if "thé" in title_lower or "café" in title_lower:
        return "☕"
    if "débarrasser" in title_lower:
        return "🧹"
    if "addition" in title_lower or "récapitulatif" in title_lower:
        return "🧾"
    if "commande" in title_lower:
        return "📝"
    if "installer" in title_lower:
        return "🪑"
    if "libérer" in title_lower:
        return "✅"
    if "supplément" in title_lower:
        return "➕"

    return "📋"


def get_task_visual_state(service, *, claimed=False, ready_at=None):
    if claimed:
        return "claimed"

    if ready_at:
        elapsed = (timezone.now() - ready_at).total_seconds()
        if elapsed > OVERDUE_MINUTES * 60:
            return "overdue"
        return "pending"

    if service.elapsed_seconds > OVERDUE_MINUTES * 60:
        return "overdue"

    return "pending"


def _workflow_task_is_claimed(service):
    return bool(service.task_claimed_at)


def _workflow_claim_matches_user(service, user):
    if not _workflow_task_is_claimed(service):
        return False

    if not user or not user.is_authenticated:
        return True

    if not service.task_claimed_by_id:
        return True

    return service.task_claimed_by_id == user.id


def serialize_workflow_task(
    service,
    order,
    *,
    current_user=None,
    workflow_snapshot=None,
):
    if workflow_snapshot is None:
        from riad.services.prefetch import (
            load_order_for_details,
            prefetch_workflow_items_for_orders,
        )

        order = load_order_for_details(order)
        if order:
            prefetch_workflow_items_for_orders(
                [order],
                services_by_order_id={order.id: service},
            )
        details = build_table_details(service.table, service, order)
    else:
        read_ctx = workflow_snapshot.get("_ctx")
        if read_ctx:
            workflow_status = read_ctx.get_workflow_status()
        else:
            workflow_status = resolve_workflow_status(service, order) if order else service.status
        workflow = get_workflow_step(workflow_status)
        category_action = workflow_snapshot.get("table_action")
        data = service.to_dict()
        details = {
            "action": (
                category_action.get("title")
                if category_action
                else workflow.get("title")
            ),
            "icon": (
                category_action.get("icon")
                if category_action
                else workflow.get("icon", data.get("icon"))
            ),
            "elapsed_seconds": data.get("elapsed_seconds") or 0,
            "next_action": dict(category_action) if category_action else {
                "title": workflow.get("title"),
                "button": workflow.get("button"),
                "type": workflow.get("type"),
                "sections": workflow.get("sections"),
            },
        }
        if service.status == "ordering":
            has_draft = bool(order and order.has_wizard_draft)
            details["next_action"] = {
                "title": "Finaliser la commande",
                "button": "Reprendre la commande" if has_draft else "Continuer la commande",
                "type": "open_commande",
            }
        elif service.status == "bill_requested":
            details["next_action"] = {
                "title": "Paiement",
                "button": "",
                "type": "payment",
            }

    next_action = details.get("next_action") or {}

    title = next_action.get("title") or details.get("action") or "Action"
    icon = details.get("icon") or "arrow_forward"
    action_type = next_action.get("type", "action")
    pre_ticket_url = next_action.get("pre_ticket_url")
    elapsed_seconds = details.get("elapsed_seconds") or 0

    if service.status == "coffee_cleared":
        title = "Apporter l'addition"
        icon = "receipt_long"
        action_type = "action"
        pre_ticket_url = None

    claimed = _workflow_task_is_claimed(service)
    claimed_by_me = _workflow_claim_matches_user(service, current_user)

    waiting_since = service.status_started_at
    sort_timestamp = waiting_since.timestamp() if waiting_since else 0

    priority_score = get_task_priority_score(
        service=service,
        order=order,
        title=title,
        action_type=action_type,
    )

    elapsed_label = format_elapsed_since(elapsed_seconds)
    is_order_task = service.status in ("installed", "ordering")
    take_order_task = is_take_order_task(title, service)
    served_since_prefix = (
        next_action.get("served_since_prefix")
        or get_clearing_served_prefix(service, title)
    )
    served_since_at = None
    served_since_label = next_action.get("served_since_label")
    installed_at = None
    installed_since_label = None
    installed_since_seconds = None

    if take_order_task and service.installed_at:
        installed_at = service.installed_at
        installed_since_seconds = max(
            int((timezone.now() - installed_at).total_seconds()),
            0,
        )
        installed_since_label = format_installed_since_label(
            installed_since_seconds
        )

    if next_action.get("served_since_at"):
        served_since_at = next_action["served_since_at"]
        if isinstance(served_since_at, str):
            from django.utils.dateparse import parse_datetime

            served_since_at = parse_datetime(served_since_at) or served_since_at
    elif served_since_prefix:
        # Fallback : max(served_at) via snapshot / items si disponible
        served_since_at = service.status_started_at

    if served_since_prefix and served_since_at and not served_since_label:
        if hasattr(served_since_at, "timestamp"):
            elapsed = max(int((timezone.now() - served_since_at).total_seconds()), 0)
        else:
            elapsed = service.elapsed_seconds
        served_since_label = format_served_since_label(served_since_prefix, elapsed)
    elif served_since_label and not served_since_at and next_action.get("served_since_at"):
        served_since_at = next_action["served_since_at"]

    return {
        "id": service.id,
        "task_key": "workflow",
        "extra_ticket_id": None,
        "table_numero": service.table.numero,
        "room": service.table.room.name,
        "title": title,
        "emoji": get_task_emoji(icon, title, action_type=action_type),
        "action_type": action_type,
        "pre_ticket_url": pre_ticket_url,
        "serve_category": None,
        "lines": [],
        "items": [],
        "item_ids": [],
        "is_order_task": is_order_task,
        "commande_url": (
            f"/riad/table/{service.table.numero}/commande/?from=tasks"
            if is_order_task
            else None
        ),
        "priority_score": priority_score,
        "ready_at": None,
        "ready_label": None,
        "elapsed_seconds": elapsed_seconds,
        "elapsed_label": elapsed_label if not take_order_task else None,
        "installed_at": installed_at.isoformat() if installed_at else None,
        "installed_since_label": installed_since_label,
        "installed_since_seconds": installed_since_seconds,
        "served_since_at": (
            served_since_at.isoformat()
            if hasattr(served_since_at, "isoformat")
            else served_since_at
        ),
        "served_since_prefix": served_since_prefix,
        "served_since_label": served_since_label,
        "sort_timestamp": sort_timestamp,
        "claimed": claimed,
        "claimed_by_me": claimed_by_me,
        "claimed_by_id": service.task_claimed_by_id,
        "visual_state": get_task_visual_state(service, claimed=claimed),
    }


def serialize_serve_item_task(service, serve_task, *, current_user=None):
    ready_at = serve_task["ready_at"]
    sort_timestamp = ready_at.timestamp() if ready_at else 0
    serve_category = serve_task.get("serve_category")
    priority_score = get_task_priority_score(
        service=service,
        order=None,
        title=serve_task["title"],
        action_type="serve_items",
        serve_category=serve_category,
    )
    ready_label = format_ready_since(ready_at)
    task_items = serve_task.get("items") or serve_task.get("lines") or []

    if serve_category:
        task_type = f"serve_{serve_category}"
    elif serve_task.get("extra_ticket_id"):
        task_type = "serve_extra"
    else:
        task_type = "serve_items"

    return {
        "id": service.id,
        "task_key": serve_task["task_key"],
        "extra_ticket_id": serve_task.get("extra_ticket_id"),
        "table_id": service.table_id,
        "table_numero": service.table.numero,
        "table_name": f"Table {service.table.numero}",
        "room": service.table.room.name,
        "title": serve_task["title"],
        "label": serve_task.get("label") or serve_task["title"],
        "emoji": get_task_emoji(
            "restaurant",
            serve_task["title"],
            action_type="serve_items",
            serve_category=serve_category,
        ),
        "action_type": "serve_items",
        "task_type": task_type,
        "pre_ticket_url": None,
        "serve_category": serve_category,
        "lines": task_items,
        "items": task_items,
        "item_ids": serve_task.get("item_ids") or [],
        "is_order_task": False,
        "commande_url": None,
        "priority_score": priority_score,
        "ready_at": ready_at.isoformat() if ready_at else None,
        "ready_label": ready_label,
        "elapsed_seconds": None,
        "elapsed_label": ready_label,
        "sort_timestamp": sort_timestamp,
        "claimed": serve_task.get("claimed", False),
        "claimed_by_me": serve_task.get("claimed_by_me", False),
        "claimed_by_id": serve_task.get("claimed_by_id"),
        "visual_state": get_task_visual_state(
            service,
            claimed=serve_task.get("claimed", False),
            ready_at=ready_at,
        ),
    }


def build_workflow_server_task(service, order, current_user=None, *, workflow_snapshot=None):
    if service.status in INACTIVE_STATUSES:
        return None

    if service.status in POST_MEAL_WAITING_STATUSES:
        return None

    # Phase paiement : pas de tâche workflow — le drawer affiche le bloc paiement.
    if service.status == "bill_requested":
        return None

    if workflow_snapshot is None and order:
        workflow_snapshot = get_service_workflow_snapshot(service, order, context="tasks")

    read_ctx = workflow_snapshot.get("_ctx") if workflow_snapshot else None
    if read_ctx:
        workflow_status = read_ctx.get_workflow_status()
    else:
        workflow_status = resolve_workflow_status(service, order) if order else service.status
    workflow = get_workflow_step(workflow_status)

    if workflow.get("type") == "products":
        return None

    if workflow.get("icon") == "cleaning_services":
        allowed = (
            workflow_snapshot.get("is_clear_task_allowed")
            if workflow_snapshot
            else (order and is_clear_task_allowed(service, order))
        )
        if not order or not allowed:
            return None

    return serialize_workflow_task(
        service,
        order,
        current_user=current_user,
        workflow_snapshot=workflow_snapshot,
    )


def build_tasks_for_service(service, order, current_user=None):
    tasks = []
    workflow_snapshot = (
        get_service_workflow_snapshot(service, order, context="tasks")
        if order
        else None
    )

    for serve_task in build_serve_tasks_for_service(
        service,
        order=order,
        current_user=current_user,
        workflow_snapshot=workflow_snapshot,
    ):
        tasks.append(
            serialize_serve_item_task(service, serve_task, current_user=current_user)
        )

    workflow_task = build_workflow_server_task(
        service,
        order,
        current_user=current_user,
        workflow_snapshot=workflow_snapshot,
    )
    if workflow_task:
        tasks.append(workflow_task)

    return tasks


def filter_tasks_for_user(tasks, user):
    serve_tasks = [task for task in tasks if task.get("action_type") == "serve_items"]
    workflow_tasks = [task for task in tasks if task.get("action_type") != "serve_items"]

    filtered_serve = filter_serve_tasks_for_user(serve_tasks, user)
    filtered_workflow = []

    for task in workflow_tasks:
        if task.get("claimed") and not task.get("claimed_by_me"):
            if user and user.is_authenticated and task.get("claimed_by_id"):
                continue
        filtered_workflow.append(task)

    return filtered_serve + filtered_workflow


def sort_server_tasks(tasks):
    return sorted(tasks, key=task_sort_key)


def build_task_list(services_with_orders, current_user=None):
    tasks = []

    for service, order in services_with_orders:
        tasks.extend(build_tasks_for_service(service, order, current_user=current_user))

    tasks = filter_tasks_for_user(tasks, current_user)
    return sort_server_tasks(tasks)


def iter_active_services_with_orders():
    from riad.models import DiningOrder, TableService

    services = (
        TableService.objects
        .select_related("table", "table__room", "task_claimed_by")
        .exclude(status__in=INACTIVE_STATUSES)
    )

    orders_by_service_id = {
        order.service_id: order
        for order in DiningOrder.objects.filter(service__in=services)
    }

    for service in services:
        yield service, orders_by_service_id.get(service.id)
