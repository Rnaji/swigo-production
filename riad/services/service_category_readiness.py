import logging

from django.conf import settings
from django.utils import timezone

from riad.models import KitchenTicketItem
from riad.services.order_content import (
    COFFEE_SECTIONS,
    DESSERT_SECTIONS,
    DRINK_SECTIONS,
    MAIN_SECTIONS,
    SERVICE_STEPS,
    STARTER_SECTIONS,
    _order_has_sections,
    resolve_workflow_status,
)
from riad.services.workflow import get_workflow_step

SERVICE_CATEGORIES = (
    "drinks",
    "starters",
    "mains",
    "desserts",
    "coffee",
)

CATEGORY_SECTIONS = {
    "drinks": DRINK_SECTIONS,
    "starters": STARTER_SECTIONS,
    "mains": MAIN_SECTIONS,
    "desserts": DESSERT_SECTIONS,
    "coffee": COFFEE_SECTIONS,
}

SERVE_WORKFLOW_STATUS_TO_CATEGORY = {
    "ordered": "drinks",
    "drinks_served": "starters",
    "starters_cleared": "mains",
    "mains_cleared": "desserts",
    "desserts_cleared": "coffee",
}

CATEGORY_SERVED_STATUS = {
    "drinks": "drinks_served",
    "starters": "starters_served",
    "mains": "mains_served",
    "desserts": "desserts_served",
    "coffee": "coffee_served",
}

STATUS_MARKS_CATEGORY_SERVED = {
    served_status: category
    for category, served_status in CATEGORY_SERVED_STATUS.items()
}

CLEARING_STATUS_TO_CATEGORY = STATUS_MARKS_CATEGORY_SERVED.copy()

CATEGORY_SERVE_PHASE_STATUS = {
    "drinks": "ordered",
    "starters": "drinks_served",
    "mains": "starters_cleared",
    "desserts": "mains_cleared",
    "coffee": "desserts_cleared",
}

CATEGORY_CLEARED_STATUS = {
    "starters": "starters_cleared",
    "mains": "mains_cleared",
    "desserts": "desserts_cleared",
    "coffee": "coffee_cleared",
}

ACTIVE_TICKET_STATUSES = ("pending", "preparing", "ready")

WORKFLOW_TICKET_STATUSES = ACTIVE_TICKET_STATUSES + ("served",)

logger = logging.getLogger(__name__)

PHASE_NOT_APPLICABLE = "not_applicable"
PHASE_WAITING_KITCHEN = "waiting_kitchen"
PHASE_READY_TO_SERVE = "ready_to_serve"
PHASE_SERVED_WAITING_CLEAR = "served_waiting_clear"
PHASE_READY_TO_CLEAR = "ready_to_clear"
PHASE_CLEARED = "cleared"

CATEGORY_DISPLAY_CONFIG = {
    "drinks": {
        "preparing_title": "Boissons en préparation",
        "serve_title": "Servir les boissons",
        "serve_button": "Boissons servies",
        "served_title": "Boissons servies",
        "clear_title": None,
        "clear_button": None,
        "icon_serve": "local_bar",
        "has_clear_step": False,
    },
    "starters": {
        "preparing_title": "Entrées en préparation",
        "serve_title": "Servir les entrées",
        "serve_button": "Entrées servies",
        "served_title": "Entrées servies",
        "clear_title": "Débarrasser les entrées",
        "clear_button": "Entrées débarrassées",
        "icon_serve": "restaurant_menu",
        "has_clear_step": True,
    },
    "mains": {
        "preparing_title": "Plats en préparation",
        "serve_title": "Servir les plats",
        "serve_button": "Plats servis",
        "served_title": "Plats servis",
        "clear_title": "Débarrasser les plats",
        "clear_button": "Plats débarrassés",
        "icon_serve": "restaurant",
        "has_clear_step": True,
    },
    "desserts": {
        "preparing_title": "Desserts en préparation",
        "serve_title": "Servir les desserts",
        "serve_button": "Desserts servis",
        "served_title": "Desserts servis",
        "clear_title": "Débarrasser les desserts",
        "clear_button": "Desserts débarrassés",
        "icon_serve": "icecream",
        "has_clear_step": True,
    },
    "coffee": {
        "preparing_title": "Thés / cafés en préparation",
        "serve_title": "Servir les thés / cafés",
        "serve_button": "Thés / cafés servis",
        "served_title": "Thés / cafés servis",
        "clear_title": "Débarrasser les thés / cafés",
        "clear_button": "Thés / cafés débarrassés",
        "icon_serve": "local_cafe",
        "has_clear_step": True,
    },
}

CATEGORY_NOUNS = {
    "drinks": {
        "one": "boisson",
        "many": "boissons",
        "served_one": "boisson servie",
        "served_many": "boissons servies",
        "ready_one": "prête",
        "ready_many": "prêtes",
    },
    "starters": {
        "one": "entrée",
        "many": "entrées",
        "served_one": "entrée servie",
        "served_many": "entrées servies",
        "ready_one": "prête",
        "ready_many": "prêtes",
    },
    "mains": {
        "one": "plat",
        "many": "plats",
        "served_one": "plat servi",
        "served_many": "plats servis",
        "ready_one": "prêt",
        "ready_many": "prêts",
    },
    "desserts": {
        "one": "dessert",
        "many": "desserts",
        "served_one": "dessert servi",
        "served_many": "desserts servis",
        "ready_one": "prêt",
        "ready_many": "prêts",
    },
    "coffee": {
        "one": "thé/café",
        "many": "thés/cafés",
        "served_one": "thé/café servi",
        "served_many": "thés/cafés servis",
        "ready_one": "prêt",
        "ready_many": "prêts",
    },
}


def _category_has_clear_step(category):
    return CATEGORY_DISPLAY_CONFIG.get(category, {}).get("has_clear_step", False)


def item_serve_quantity(item):
    return max(int(getattr(item, "quantity", 1) or 1), 1)


def count_category_progress(items):
    served = 0
    ready = 0
    preparing = 0
    for item in items:
        qty = item_serve_quantity(item)
        if item.is_served:
            served += qty
        elif item.is_done:
            ready += qty
        else:
            preparing += qty
    return {
        "served_count": served,
        "ready_count": ready,
        "preparing_count": preparing,
    }


def format_category_serve_title(category, count):
    nouns = CATEGORY_NOUNS.get(category) or {
        "one": "article",
        "many": "articles",
    }
    noun = nouns["one"] if count <= 1 else nouns["many"]
    return f"Servir {max(int(count), 0)} {noun}"


def format_category_progress_label(category, *, served=0, ready=0, preparing=0):
    nouns = CATEGORY_NOUNS.get(category)
    if not nouns:
        return None

    parts = []
    if served > 0:
        label = nouns["served_one"] if served == 1 else nouns["served_many"]
        parts.append(f"{served} {label}")
    if ready > 0:
        adj = nouns["ready_one"] if ready == 1 else nouns["ready_many"]
        parts.append(f"{ready} {adj}")
    if preparing > 0:
        parts.append(f"{preparing} en préparation")

    if not parts:
        return None
    return " • ".join(parts)


def get_category_phase_display(category, phase, state=None):
    config = CATEGORY_DISPLAY_CONFIG.get(category)
    if not config or phase in (PHASE_NOT_APPLICABLE, PHASE_CLEARED):
        return None

    sections = list(CATEGORY_SECTIONS.get(category, ()))
    progress = count_category_progress((state or {}).get("items") or [])
    served = progress["served_count"]
    ready = progress["ready_count"]
    preparing = progress["preparing_count"]

    if phase == PHASE_WAITING_KITCHEN:
        progress_title = format_category_progress_label(
            category,
            served=served,
            preparing=preparing,
        )
        title = progress_title if served > 0 else config["preparing_title"]
        return {
            "title": title,
            "button": "En attente cuisine",
            "type": "wait",
            "icon": config["icon_serve"],
            "sections": sections,
        }

    if phase == PHASE_READY_TO_SERVE:
        action = {
            "title": format_category_serve_title(category, ready or 1),
            "button": config["serve_button"],
            "type": "products",
            "icon": config["icon_serve"],
            "sections": sections,
        }
        progress_label = format_category_progress_label(
            category,
            served=served,
            ready=ready,
            preparing=preparing,
        )
        if progress_label and (served > 0 or preparing > 0):
            action["progress_label"] = progress_label
        return action

    if phase == PHASE_SERVED_WAITING_CLEAR:
        return {
            "title": config["served_title"],
            "button": "Attendre avant de débarrasser",
            "type": "wait",
            "icon": config["icon_serve"],
            "sections": [],
        }

    if phase == PHASE_READY_TO_CLEAR and config["clear_title"]:
        return {
            "title": config["clear_title"],
            "button": config["clear_button"],
            "type": "action",
            "icon": "cleaning_services",
            "sections": [],
        }

    return None


def _status_index(status):
    try:
        return SERVICE_STEPS.index(status)
    except ValueError:
        return -1


def kitchen_item_section_name(item):
    if item.section_id and item.section:
        return item.section.name

    if item.product_id and item.product and item.product.category_id:
        return item.product.category.name

    return None


def kitchen_item_belongs_to_category(item, category):
    section_name = kitchen_item_section_name(item)

    if not section_name:
        return False

    if section_name == "Supplément libre":
        return False

    return section_name in CATEGORY_SECTIONS[category]


def get_category_kitchen_items(order, category):
    if not order:
        return []

    items = (
        KitchenTicketItem.objects
        .filter(
            ticket__order=order,
            ticket__status__in=ACTIVE_TICKET_STATUSES,
        )
        .select_related("section", "product", "product__category", "ticket")
    )

    return [item for item in items if kitchen_item_belongs_to_category(item, category)]


def get_category_workflow_items(order, category, service=None):
    if not order:
        return []

    items = (
        KitchenTicketItem.objects
        .filter(
            ticket__order=order,
            ticket__status__in=WORKFLOW_TICKET_STATUSES,
        )
        .select_related("section", "product", "product__category", "ticket")
    )

    if service is not None:
        items = items.filter(ticket__service=service)

    return [item for item in items if kitchen_item_belongs_to_category(item, category)]


def is_category_fully_served(service, order, category):
    """
    True uniquement lorsque toutes les lignes actives de la catégorie sont
    prêtes (is_done) et servies (is_served).
    """
    if not service or not order or category not in CATEGORY_SECTIONS:
        return False

    items = get_category_workflow_items(order, category, service=service)
    if not items:
        return False

    return all(item.is_done and item.is_served for item in items)


def order_has_category_choices(order, category):
    sections = CATEGORY_SECTIONS.get(category, frozenset())
    return _order_has_sections(order, sections)


def is_category_already_served(service, category):
    served_status = CATEGORY_SERVED_STATUS.get(category)
    if not served_status or not service:
        return False

    return _status_index(service.status) >= _status_index(served_status)


def get_pending_serve_category(service, order):
    if not service or not order:
        return None

    workflow_status = resolve_workflow_status(service, order)
    workflow = get_workflow_step(workflow_status)

    if workflow.get("type") != "products":
        return None

    return SERVE_WORKFLOW_STATUS_TO_CATEGORY.get(workflow_status)


def is_service_category_ready(order, category, service=None):
    """
    True uniquement lorsque la catégorie est entièrement prête à servir :
    - au moins une ligne commandée dans la catégorie ;
    - au moins une ligne active en Cuisine / Office pour cette catégorie ;
    - toutes ces lignes sont marquées Fait ;
    - l'étape de service principale n'a pas déjà été validée.
    """
    if category not in CATEGORY_SECTIONS:
        return False

    if not order or not order.is_sent_to_kitchen:
        return False

    if not order_has_category_choices(order, category):
        return False

    if service and is_category_already_served(service, category):
        return False

    if service:
        pending_category = get_pending_serve_category(service, order)
        if pending_category != category:
            return False

    kitchen_items = get_category_kitchen_items(order, category)

    if not kitchen_items:
        return False

    return all(item.is_done for item in kitchen_items)


def get_category_ready_at(order, category):
    """
    Moment où tous les articles actifs de la catégorie sont devenus prêts.
    """
    kitchen_items = get_category_kitchen_items(order, category)

    if not kitchen_items or not all(item.is_done for item in kitchen_items):
        return None

    done_times = [item.done_at for item in kitchen_items if item.done_at]

    if len(done_times) == len(kitchen_items):
        return max(done_times)

    sent_times = [
        item.ticket.sent_at
        for item in kitchen_items
        if item.ticket.sent_at
    ]
    if sent_times:
        return max(sent_times)

    return timezone.now()


def get_extra_ticket_ready_at(ticket):
    items = list(ticket.items.all())
    if not items or not all(item.is_done for item in items):
        return None

    done_times = [item.done_at for item in items if item.done_at]
    if len(done_times) == len(items):
        return max(done_times)

    if ticket.sent_at:
        return ticket.sent_at

    return timezone.now()


def is_serve_action_kitchen_gated(workflow_status, workflow):
    if workflow.get("type") != "products":
        return False

    return workflow_status in SERVE_WORKFLOW_STATUS_TO_CATEGORY


def infer_ticket_category(ticket):
    for item in ticket.items.all():
        section_name = kitchen_item_section_name(item)
        if not section_name or section_name == "Supplément libre":
            continue

        for category, sections in CATEGORY_SECTIONS.items():
            if section_name in sections:
                return category

    return None


def get_ready_extra_serve_tasks(service, order):
    if not order or not order.is_sent_to_kitchen:
        return []

    from riad.models import KitchenTicket

    tasks = []
    tickets = (
        KitchenTicket.objects
        .filter(
            order=order,
            ticket_type="extra",
            status__in=ACTIVE_TICKET_STATUSES,
        )
        .prefetch_related("items__section", "items__product__category")
    )

    for ticket in tickets:
        items = list(ticket.items.all())
        if not items or not all(item.is_done for item in items):
            continue

        category = infer_ticket_category(ticket)
        if category and not is_category_already_served(service, category):
            continue

        if category:
            section_label = next(iter(CATEGORY_SECTIONS[category])).lower()
            title = f"Servir l'extra {section_label}"
        else:
            title = "Servir le supplément"

        tasks.append({
            "category": category,
            "extra_ticket_id": ticket.id,
            "title": title,
            "ready_at": get_extra_ticket_ready_at(ticket),
        })

    return tasks


def get_category_items_state(service, order, category):
    items = get_category_workflow_items(order, category, service=service)
    progress = count_category_progress(items)
    return {
        "has_items": bool(items),
        "all_done": bool(items) and all(item.is_done for item in items),
        "all_served": bool(items) and all(item.is_served for item in items),
        "ready_count": progress["ready_count"],
        "served_count": progress["served_count"],
        "preparing_count": progress["preparing_count"],
        "items": items,
    }


def get_clear_task_delay_seconds(service_status):
    """Délai d'affichage carte (progress) — n'ouvre plus la tâche Débarrasser."""
    from riad.constants import SERVICE_STATUS

    config = SERVICE_STATUS.get(service_status, {})
    return int(config.get("target") or 0)


def is_clear_delay_reached(service):
    """Toujours True : le débarrassage est immédiat dès que la catégorie est servie."""
    return True


def get_category_last_served_at(items):
    served_ats = [item.served_at for item in items if getattr(item, "served_at", None)]
    if not served_ats:
        return None
    return max(served_ats)


def format_served_since_label(prefix, elapsed_seconds):
    minutes = max(int(elapsed_seconds) // 60, 0)

    if minutes <= 0:
        return f"{prefix} depuis moins d'une minute"

    if minutes == 1:
        return f"{prefix} depuis 1 min"

    return f"{prefix} depuis {minutes} min"


def build_served_since_info(category, items, *, now=None):
    """
    Temps écoulé depuis que la catégorie est entièrement servie
    (référence = max(served_at) des lignes).
    """
    if not _category_has_clear_step(category):
        return None

    last_served_at = get_category_last_served_at(items)
    if not last_served_at:
        return None

    config = CATEGORY_DISPLAY_CONFIG.get(category) or {}
    prefix = config.get("served_title")
    if not prefix:
        return None

    reference = now or timezone.now()
    elapsed_seconds = max(int((reference - last_served_at).total_seconds()), 0)

    return {
        "served_since_at": last_served_at.isoformat(),
        "served_since_prefix": prefix,
        "served_since_label": format_served_since_label(prefix, elapsed_seconds),
        "served_since_seconds": elapsed_seconds,
    }


def is_clear_task_allowed(service, order):
    category = CLEARING_STATUS_TO_CATEGORY.get(service.status)
    if not category or not order:
        return False

    if not _category_has_clear_step(category):
        return False

    if not order_has_category_choices(order, category):
        return False

    expected_served_status = CATEGORY_SERVED_STATUS.get(category)
    if service.status != expected_served_status:
        return False

    cleared_status = CATEGORY_CLEARED_STATUS.get(category)
    if not cleared_status:
        return False

    if _status_index(service.status) >= _status_index(cleared_status):
        return False

    state = get_category_items_state(service, order, category)
    if not state["has_items"]:
        return False

    if not state["all_done"] or not state["all_served"]:
        return False

    if not is_category_fully_served(service, order, category):
        return False

    return True


def get_category_phase(service, order, category):
    if not order or category not in CATEGORY_SECTIONS:
        return PHASE_NOT_APPLICABLE

    if not order_has_category_choices(order, category):
        return PHASE_NOT_APPLICABLE

    cleared_status = CATEGORY_CLEARED_STATUS.get(category)
    if cleared_status and _status_index(service.status) >= _status_index(cleared_status):
        return PHASE_CLEARED

    state = get_category_items_state(service, order, category)

    if not state["has_items"]:
        return PHASE_WAITING_KITCHEN

    if state["all_served"]:
        served_status = CATEGORY_SERVED_STATUS.get(category)
        if not served_status:
            return PHASE_NOT_APPLICABLE

        if not _category_has_clear_step(category):
            if _status_index(service.status) >= _status_index(served_status):
                return PHASE_CLEARED
            return PHASE_SERVED_WAITING_CLEAR

        if service.status == served_status and is_clear_task_allowed(service, order):
            return PHASE_READY_TO_CLEAR

        if cleared_status and _status_index(service.status) >= _status_index(cleared_status):
            return PHASE_CLEARED

        if _status_index(service.status) < _status_index(served_status):
            return PHASE_SERVED_WAITING_CLEAR

        return PHASE_SERVED_WAITING_CLEAR

    # Service partiel : dès qu'une ligne est prête, elle est servable.
    if state["ready_count"] > 0:
        return PHASE_READY_TO_SERVE

    return PHASE_WAITING_KITCHEN


def reconcile_served_category_status(service, order, category):
    if not order or not service or category not in CATEGORY_SERVED_STATUS:
        return False

    if not is_category_fully_served(service, order, category):
        return False

    served_status = CATEGORY_SERVED_STATUS[category]
    if _status_index(service.status) >= _status_index(served_status):
        return False

    serve_phase = CATEGORY_SERVE_PHASE_STATUS.get(category)
    if serve_phase and _status_index(service.status) < _status_index(serve_phase):
        return False

    service.set_status(served_status)
    return True


def category_table_action_applies(service, order, category):
    if not order or not order_has_category_choices(order, category):
        return False

    serve_phase = CATEGORY_SERVE_PHASE_STATUS[category]
    workflow_status = resolve_workflow_status(service, order)
    if _status_index(workflow_status) < _status_index(serve_phase):
        return False

    cleared_status = CATEGORY_CLEARED_STATUS.get(category)
    served_status = CATEGORY_SERVED_STATUS[category]

    if cleared_status:
        if _status_index(service.status) > _status_index(cleared_status):
            return False
    elif _status_index(service.status) > _status_index(served_status):
        return False

    return True


def get_category_table_action(service, order, category):
    if not category_table_action_applies(service, order, category):
        return None

    phase = get_category_phase(service, order, category)
    if phase in (PHASE_NOT_APPLICABLE, PHASE_CLEARED):
        return None

    state = get_category_items_state(service, order, category)
    action = get_category_phase_display(category, phase, state)
    if action and phase == PHASE_READY_TO_CLEAR:
        served_info = build_served_since_info(category, state["items"])
        if served_info:
            action = {**action, **served_info}

    return action


def get_active_category_table_action(service, order):
    if not order:
        return None

    for category in SERVICE_CATEGORIES:
        action = get_category_table_action(service, order, category)
        if action:
            return action

    return None


def reconcile_category_workflows(service, order):
    if not order:
        return

    reconcile_clearing_service_status(service, order)

    for category in SERVICE_CATEGORIES:
        if not order_has_category_choices(order, category):
            continue
        reconcile_served_category_status(service, order, category)
        log_category_coherence(service, order, category)


def should_show_category_serve_task(service, order, category):
    return get_category_phase(service, order, category) == PHASE_READY_TO_SERVE


def log_category_coherence(service, order, category):
    if not settings.DEBUG or not order:
        return

    phase = get_category_phase(service, order, category)
    if phase == PHASE_NOT_APPLICABLE:
        return

    config = CATEGORY_DISPLAY_CONFIG.get(category, {})
    state = get_category_items_state(service, order, category)
    issues = []
    served_status = CATEGORY_SERVED_STATUS.get(category)
    cleared_status = CATEGORY_CLEARED_STATUS.get(category)

    if served_status and service.status == served_status and state["has_items"] and not state["all_served"]:
        issues.append(f"{category}: {served_status} but some items are not served")

    if state["items"]:
        for item in state["items"]:
            if item.is_served and not item.is_done:
                issues.append(
                    f"{category}: item {item.id} is_served=True but is_done=False"
                )

    if cleared_status and service.status == cleared_status and state["has_items"] and not state["all_served"]:
        issues.append(f"{category}: {cleared_status} but some items are not served")

    if phase == PHASE_READY_TO_CLEAR and not state["all_served"]:
        issues.append(f"{category}: clear phase but items not all served")

    if phase == PHASE_READY_TO_SERVE and state["all_served"]:
        issues.append(f"{category}: serve phase but all items already served")

    if issues:
        logger.warning(
            "%s workflow coherence issues for service %s: %s",
            config.get("serve_title", category),
            service.id,
            "; ".join(issues),
        )


# Alias rétrocompatibles
reconcile_starters_workflow = reconcile_category_workflows
get_starters_table_action = lambda service, order: get_category_table_action(service, order, "starters")
should_show_starters_serve_task = lambda service, order: should_show_category_serve_task(service, order, "starters")
log_starters_coherence = lambda service, order: log_category_coherence(service, order, "starters")


def log_serve_action_state(service, order, category, label):
    if not settings.DEBUG:
        return

    state = get_category_items_state(service, order, category)
    delay_seconds = get_clear_task_delay_seconds(service.status)
    clear_allowed = is_clear_task_allowed(service, order)

    print(
        f"{label} SERVE category={category} service.id={service.id} "
        f"status={service.status} "
        f"status_started_at={service.status_started_at} "
        f"delay={delay_seconds}s clear_allowed={clear_allowed}"
    )
    for item in state["items"]:
        print(
            f"  item id={item.id} is_done={item.is_done} is_served={item.is_served} "
            f"done_at={item.done_at} served_at={item.served_at}"
        )


def reconcile_clearing_service_status(service, order):
    """
    Corrige un statut avancé trop tôt (ex. starters_served sans lignes servies).
    """
    category = CLEARING_STATUS_TO_CATEGORY.get(service.status)
    if not category or not order:
        return False

    state = get_category_items_state(service, order, category)
    if not state["has_items"]:
        return False

    if is_category_fully_served(service, order, category):
        return False

    rollback_status = CATEGORY_SERVE_PHASE_STATUS.get(category)
    if not rollback_status or service.status == rollback_status:
        return False

    service.set_status(rollback_status)
    return True
