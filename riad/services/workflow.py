# riad/services/workflow.py

SERVER_WORKFLOW = {
    "free": {
        "title": "Installer les clients",
        "button": "Installer",
        "type": "action",
        "icon": "table_restaurant",
        "sections": [],
    },

    "installed": {
        "title": "Prendre la commande",
        "button": "Prendre la commande",
        "type": "action",
        "icon": "edit_note",
        "sections": [],
    },

    "ordering": {
        "title": "Finaliser la commande",
        "button": "Valider la commande",
        "type": "action",
        "icon": "edit_note",
        "sections": [],
    },

    "ordered": {
        "title": "Servir les boissons",
        "button": "Boissons servies",
        "type": "products",
        "icon": "local_bar",
        "sections": ["Mocktail", "Boisson", "Eau"],
    },

    "drinks_served": {
        "title": "Servir les entrées",
        "button": "Entrées servies",
        "type": "products",
        "icon": "restaurant_menu",
        "sections": ["Entrée"],
    },

    "starters_served": {
        "title": "Débarrasser les entrées",
        "button": "Entrées débarrassées",
        "type": "action",
        "icon": "cleaning_services",
        "sections": [],
    },

    "starters_cleared": {
        "title": "Servir les plats",
        "button": "Plats servis",
        "type": "products",
        "icon": "restaurant",
        "sections": ["Plat"],
    },

    "mains_served": {
        "title": "Débarrasser les plats",
        "button": "Plats débarrassés",
        "type": "action",
        "icon": "cleaning_services",
        "sections": [],
    },

    "mains_cleared": {
        "title": "Servir les desserts",
        "button": "Desserts servis",
        "type": "products",
        "icon": "icecream",
        "sections": ["Dessert"],
    },

    "desserts_served": {
        "title": "Débarrasser les desserts",
        "button": "Desserts débarrassés",
        "type": "action",
        "icon": "cleaning_services",
        "sections": [],
    },

    "desserts_cleared": {
        "title": "Servir les thés / cafés",
        "button": "Thés / cafés servis",
        "type": "products",
        "icon": "local_cafe",
        "sections": ["Thé / Café"],
    },

    "coffee_served": {
        "title": "Débarrasser les thés / cafés",
        "button": "Thés / cafés débarrassés",
        "type": "action",
        "icon": "cleaning_services",
        "sections": [],
    },

    "coffee_cleared": {
        "title": "Apporter l'addition",
        "button": "Addition demandée",
        "type": "action",
        "icon": "receipt_long",
        "sections": [],
    },

    "bill_requested": {
        "title": "Encaisser",
        "button": "Paiement effectué",
        "type": "action",
        "icon": "payments",
        "sections": [],
    },

    "paid": {
        "title": "Libérer la table",
        "button": "Table libre",
        "type": "action",
        "icon": "check_circle",
        "sections": [],
    },
}


def get_workflow_step(status):
    return SERVER_WORKFLOW.get(
        status,
        {
            "title": "Action suivante",
            "button": "Suivant",
            "type": "action",
            "icon": "arrow_forward",
            "sections": [],
        }
    )