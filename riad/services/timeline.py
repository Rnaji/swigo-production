# riad/services/timeline.py

from riad.services.order_content import SERVICE_STEPS
from riad.services.workflow_engine import get_timeline_stage_state

TIMELINE_STEPS = [
    {
        "key": "installed",
        "icon": "table_restaurant",
        "label": "Installation",
        "condition": None,
    },
    {
        "key": "ordered",
        "icon": "edit_note",
        "label": "Commande",
        "condition": None,
    },
    {
        "key": "drinks",
        "icon": "local_bar",
        "label": "Boissons",
        "condition": "has_drinks",
    },
    {
        "key": "starters",
        "icon": "restaurant_menu",
        "label": "Entrées",
        "condition": "has_starters",
    },
    {
        "key": "mains",
        "icon": "restaurant",
        "label": "Plats",
        "condition": None,
    },
    {
        "key": "desserts",
        "icon": "icecream",
        "label": "Desserts",
        "condition": "has_desserts",
    },
    {
        "key": "coffee",
        "icon": "local_cafe",
        "label": "Thé / Café",
        "condition": "has_coffee",
    },
    {
        "key": "payment",
        "icon": "payments",
        "label": "Paiement",
        "condition": None,
    },
]

STAGE_DEFINITIONS = {
    "installed": {
        "serve_status": "installed",
        "clear_status": None,
        "complete_at": "ordering",
    },
    "ordered": {
        "serve_status": "ordering",
        "clear_status": None,
        "complete_at": "ordered",
    },
    "drinks": {
        "serve_status": "drinks_served",
        "clear_status": None,
        "complete_at": "drinks_served",
    },
    "starters": {
        "serve_status": "starters_served",
        "clear_status": "starters_cleared",
    },
    "mains": {
        "serve_status": "mains_served",
        "clear_status": "mains_cleared",
    },
    "desserts": {
        "serve_status": "desserts_served",
        "clear_status": "desserts_cleared",
    },
    "coffee": {
        "serve_status": "coffee_served",
        "clear_status": "coffee_cleared",
    },
    "payment": {
        "serve_status": "bill_requested",
        "clear_status": "paid",
    },
}

WORKFLOW_ICON_TO_STAGE = {
    "table_restaurant": "installed",
    "edit_note": "ordered",
    "local_bar": "drinks",
    "restaurant_menu": "starters",
    "restaurant": "mains",
    "icecream": "desserts",
    "local_cafe": "coffee",
    "receipt_long": "payment",
}


def _status_index(status):
    try:
        return SERVICE_STEPS.index(status)
    except ValueError:
        return -1


def should_show_step(service, step):
    condition = step.get("condition")

    if not condition:
        return True

    return bool(getattr(service, condition, False))


def get_stage_visual_state(stage_key, service, order=None, *, workflow_snapshot=None):
    """
    Détermine l'état visuel d'un pictogramme de timeline via workflow_engine.
    """
    return get_timeline_stage_state(
        stage_key,
        service,
        order,
        workflow_snapshot=workflow_snapshot,
    )


def build_timeline(service, order=None, *, workflow_snapshot=None):
    timeline = []

    for step in TIMELINE_STEPS:
        if not should_show_step(service, step):
            continue

        key = step["key"]

        timeline.append({
            "key": key,
            "icon": step["icon"],
            "label": step["label"],
            "state": get_stage_visual_state(
                key,
                service,
                order,
                workflow_snapshot=workflow_snapshot,
            ),
        })

    return timeline
