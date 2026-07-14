# riad/services/timeline.py

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


STEP_STATES_BY_STATUS = {
    "free": {},

    "installed": {
        "installed": "action",
    },

    "ordering": {
        "installed": "done",
        "ordered": "action",
    },

    "ordered": {
        "installed": "done",
        "ordered": "done",
        "drinks": "action",
    },

    "drinks_served": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "action",
    },

    "starters_served": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "action",
    },

    "starters_cleared": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "action",
    },

    "mains_served": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "action",
    },

    "mains_cleared": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "action",
    },

    "desserts_served": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "done",
        "coffee": "action",
    },

    "desserts_cleared": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "done",
        "coffee": "action",
    },

    "coffee_served": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "done",
        "coffee": "done",
        "payment": "action",
    },

    "coffee_cleared": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "done",
        "coffee": "done",
        "payment": "action",
    },

    "bill_requested": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "done",
        "coffee": "done",
        "payment": "action",
    },

    "paid": {
        "installed": "done",
        "ordered": "done",
        "drinks": "done",
        "starters": "done",
        "mains": "done",
        "desserts": "done",
        "coffee": "done",
        "payment": "done",
    },
}


def should_show_step(service, step):
    condition = step.get("condition")

    if not condition:
        return True

    return bool(getattr(service, condition, False))


def build_timeline(service):
    status_map = STEP_STATES_BY_STATUS.get(service.status, {})

    timeline = []

    for step in TIMELINE_STEPS:
        if not should_show_step(service, step):
            continue

        key = step["key"]

        timeline.append({
            "key": key,
            "icon": step["icon"],
            "label": step["label"],
            "state": status_map.get(key, "future"),
        })

    return timeline