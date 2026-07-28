from django.urls import path
from . import views
from . import backoffice_views

app_name = "riad"

urlpatterns = [
    # ==========================
    # PAGES
    # ==========================

    path("salle/", views.salle, name="salle"),
    path("tasks/", views.tasks_view, name="tasks"),
    path("kitchen/", views.kitchen_view, name="kitchen"),
    path("kitchen/item/<int:item_id>/toggle/", views.api_toggle_kitchen_item, name="api_toggle_kitchen_item"),
    path("kitchen/ticket/<int:ticket_id>/mark-all/", views.api_mark_all_ticket_items, name="api_mark_all_ticket_items"),
    path("kitchen/ticket/<int:ticket_id>/close/", views.api_close_kitchen_ticket, name="api_close_kitchen_ticket"),
    path("table/<int:table_id>/install/", views.install_table, name="install_table"),
    path("table/<int:numero>/commande/", views.commande_table, name="commande_table"),

    # ==========================
    # API SALLE
    # ==========================

    path("api/salle/", views.api_salle, name="api_salle"),
    path("api/tasks/", views.api_tasks, name="api_tasks"),
    path("api/tasks/<int:service_id>/claim/", views.api_task_claim, name="api_task_claim"),
    path("api/tasks/<int:service_id>/release/", views.api_task_release, name="api_task_release"),
    path("api/tasks/<int:service_id>/complete/", views.api_task_complete, name="api_task_complete"),
    path("api/tasks/extra/<int:ticket_id>/serve/", views.api_task_serve_extra, name="api_task_serve_extra"),
    path("api/table/<int:numero>/", views.api_table_detail, name="api_table_detail"),
    path("api/table/<int:numero>/details/", views.api_table_details, name="api_table_details"),
    path("api/table/<int:numero>/install/", views.api_install_table, name="api_install_table"),
    path("api/table/<int:numero>/next/", views.api_next_step, name="api_next_step"),

    # ==========================
    # API COMMANDE
    # ==========================

    path("api/table/<int:numero>/order/start/", views.api_start_order, name="api_start_order"),
    path("api/table/<int:numero>/draft/", views.api_save_wizard_draft, name="api_save_wizard_draft"),
    path("api/table/<int:numero>/covers/", views.api_update_covers, name="api_update_covers"),
    path("api/table/<int:numero>/guest/add/", views.api_add_order_guest, name="api_add_order_guest"),
    path(
        "api/table/<int:numero>/guest/delete/",
        views.api_delete_order_guest,
        name="api_delete_order_guest",
    ),
    path("api/table/<int:numero>/send-kitchen/", views.api_send_order_to_kitchen, name="api_send_order_to_kitchen"),
    path("api/table/<int:numero>/cancel-order/", views.api_cancel_order, name="api_cancel_order"),
    path("api/table/<int:numero>/add-item/", views.api_add_item, name="api_add_item"),
    path("api/table/<int:numero>/add-manual-extra/", views.api_add_manual_extra, name="api_add_manual_extra"),
    path("api/table/<int:numero>/choice/<int:choice_id>/delete/", views.api_delete_choice, name="api_delete_choice"),

    path("api/menu/<int:menu_id>/", views.api_menu, name="api_menu"),
    path("api/products/catalog/", views.api_products_catalog, name="api_products_catalog"),
    path("api/products/categories/", views.api_product_categories, name="api_product_categories"),


    path("caisse/<int:table_id>/", views.cashier_view, name="cashier"),
    path("table/<int:table_id>/pre-ticket/", views.pre_ticket_view, name="pre_ticket"),
    path("api/table/<int:numero>/mark-paid-external/", views.api_mark_paid_external_cashier, name="api_mark_paid_external"),
    path("api/payment/", views.create_payment, name="create_payment"),
    path(
        "api/payment/<int:payment_id>/delete/",
        views.delete_internal_payment,
        name="delete_internal_payment",
    ),

    # ==========================
    # BACK OFFICE
    # ==========================

    path("backoffice/", backoffice_views.dashboard, name="backoffice_dashboard"),
    path("backoffice/tickets/", backoffice_views.ticket_history, name="backoffice_tickets"),
    path(
        "backoffice/tickets/<int:order_id>/",
        backoffice_views.ticket_detail,
        name="backoffice_ticket_detail",
    ),
    path(
        "backoffice/tickets/<int:order_id>/pre-ticket/",
        backoffice_views.ticket_pre_ticket,
        name="backoffice_ticket_pre_ticket",
    ),
    path(
        "backoffice/statistiques/",
        backoffice_views.statistics,
        name="backoffice_statistics",
    ),
    path("backoffice/produits/", backoffice_views.products, name="backoffice_products"),
    path(
        "backoffice/export/tickets.csv",
        backoffice_views.export_tickets,
        name="backoffice_export_tickets",
    ),
]