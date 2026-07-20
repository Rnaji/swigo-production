# riad/constants.py

SERVICE_STATUS = {

    "free": {
        "label": "Libre",
        "action": "Nouvelle table",
        "icon": "table_restaurant",
        "target": None,
    },

    "reserved": {
        "label": "Réservée",
        "action": "Attendre les clients",
        "icon": "event_seat",
        "target": None,
    },

    "installed": {
        "label": "Clients installés",
        "action": "Prendre la commande",
        "icon": "menu_book",
        "target": 180,      # 3 min
    },

    "ordering": {
        "label": "Prise de commande",
        "action": "Terminer la commande",
        "icon": "edit_note",
        "target": 300,      # 5 min
    },

    "ordered": {
        "label": "Commande prise",
        "action": "Cuisine",
        "icon": "restaurant",
        "target": 1200,     # 20 min
    },

    "drinks_served": {
        "label": "Boissons servies",
        "action": "Servir les entrées",
        "icon": "local_bar",
        "target": 300,      # 5 min
    },

    "starters_served": {
        "label": "Entrées servies",
        "action": "Débarrasser les entrées",
        "icon": "cleaning_services",
        "target": 420,      # 7 min
    },

    "starters_cleared": {
        "label": "Entrées débarrassées",
        "action": "Servir les plats",
        "icon": "restaurant_menu",
        "target": 300,      # 5 min
    },

    "mains_served": {
        "label": "Plats servis",
        "action": "Débarrasser les plats",
        "icon": "cleaning_services",
        "target": 900,      # 15 min
    },

    "mains_cleared": {
        "label": "Plats débarrassés",
        "action": "Servir les desserts",
        "icon": "icecream",
        "target": 300,      # 5 min
    },

    "desserts_served": {
        "label": "Desserts servis",
        "action": "Débarrasser les desserts",
        "icon": "cleaning_services",
        "target": 600,      # 10 min
    },

    "desserts_cleared": {
        "label": "Desserts débarrassés",
        "action": "Servir le thé / café",
        "icon": "local_cafe",
        "target": 300,      # 5 min
    },

    "coffee_served": {
        "label": "Thé / Café servis",
        "action": "Débarrasser",
        "icon": "cleaning_services",
        "target": 600,      # 10 min
    },

    "coffee_cleared": {
        "label": "Thé / Café débarrassés",
        "action": "Proposer l'addition",
        "icon": "receipt_long",
        "target": 180,      # 3 min
    },

    "bill_requested": {
        "label": "Addition demandée",
        "action": "Présenter le récapitulatif",
        "icon": "receipt_long",
        "target": 300,      # 5 min
    },

    "paid": {
        "label": "Addition réglée",
        "action": "Libérer la table",
        "icon": "check_circle",
        "target": 180,      # 3 min
    },

}