from django.urls import path
from . import views

app_name = "riad"

urlpatterns = [
    # ==========================
    # PAGES
    # ==========================

    path("salle/", views.salle, name="salle"),
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
    path("api/table/<int:numero>/", views.api_table_detail, name="api_table_detail"),
    path("api/table/<int:numero>/details/", views.api_table_details, name="api_table_details"),
    path("api/table/<int:numero>/install/", views.api_install_table, name="api_install_table"),
    path("api/table/<int:numero>/next/", views.api_next_step, name="api_next_step"),

    # ==========================
    # API COMMANDE
    # ==========================

    path("api/table/<int:numero>/order/start/", views.api_start_order, name="api_start_order"),
    path("api/table/<int:numero>/draft/", views.api_save_wizard_draft, name="api_save_wizard_draft"),
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
    path("api/payment/", views.create_payment, name="create_payment"),]