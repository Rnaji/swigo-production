from django.contrib import admin
from .models import DiningTable, Reservation, TableService
from .models import DiningOrder, GuestOrder, GuestChoice
from .models import (
    ProductCategory,
    Product,
    Menu,
    MenuSection,
    MenuSectionItem,
)


@admin.register(DiningTable)
class DiningTableAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "room",
        "grid_x",
        "grid_y",
        "is_active",
    )

    list_editable = (
        "room",
        "grid_x",
        "grid_y",
        "is_active",
    )

    list_filter = (
        "room",
        "is_active",
    )

    search_fields = (
        "numero",
    )

    ordering = (
        "room__order",
        "grid_y",
        "grid_x",
    )

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "table",
        "personnes",
        "date_heure",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "nom",
        "telephone",
    )

    ordering = (
        "date_heure",
    )


@admin.register(TableService)
class TableServiceAdmin(admin.ModelAdmin):
    list_display = (
        "table",
        "status",
        "reservation",
        "status_started_at",
    )

    list_filter = (
        "status",
    )

    ordering = (
        "table",
    )


class GuestChoiceInline(admin.TabularInline):
    model = GuestChoice
    extra = 0


class GuestOrderInline(admin.TabularInline):
    model = GuestOrder
    extra = 0


@admin.register(DiningOrder)
class DiningOrderAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "is_sent_to_kitchen",
        "created_at",
    )
    list_filter = (
        "is_sent_to_kitchen",
    )


@admin.register(GuestOrder)
class GuestOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "guest_number",
        "menu",
        "kitchen_note",
    )

    list_filter = (
        "menu",
    )

    search_fields = (
        "order__service__table__numero",
    )

    ordering = (
        "order",
        "guest_number",
    )


@admin.register(GuestChoice)
class GuestChoiceAdmin(admin.ModelAdmin):
    list_display = (
        "guest",
        "section",
        "product",
        "quantity",
        "note",
    )

    list_filter = (
        "section",
        "product",
    )

    search_fields = (
        "product__name",
        "guest__order__service__table__numero",
    )

    ordering = (
        "guest",
        "section__order",
    )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    list_editable = ("price", "is_active")
    search_fields = ("name",)
    ordering = ("category__order", "name")


class MenuSectionInline(admin.TabularInline):
    model = MenuSection
    extra = 0


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "order", "is_active")
    list_editable = ("price", "order", "is_active")
    inlines = [MenuSectionInline]
    ordering = ("order",)


class MenuSectionItemInline(admin.TabularInline):
    model = MenuSectionItem
    extra = 0


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ("menu", "name", "order", "required")
    list_filter = ("menu",)
    list_editable = ("order", "required")
    inlines = [MenuSectionItemInline]
    ordering = ("menu__order", "order")


@admin.register(MenuSectionItem)
class MenuSectionItemAdmin(admin.ModelAdmin):
    list_display = ("section", "product", "order")
    list_filter = ("section__menu", "section")
    ordering = ("section__menu__order", "section__order", "order")