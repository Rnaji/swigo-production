from decimal import Decimal

from django.db import migrations, models


def backfill_applied_vat_rates(apps, schema_editor):
    GuestOrder = apps.get_model("riad", "GuestOrder")
    GuestChoice = apps.get_model("riad", "GuestChoice")
    Product = apps.get_model("riad", "Product")

    menu_rate = Decimal("10.00")

    GuestOrder.objects.filter(menu_applied_vat_rate__isnull=True).update(
        menu_applied_vat_rate=menu_rate
    )

    product_rates = {
        product.pk: product.vat_rate
        for product in Product.objects.all()
    }

    for choice in GuestChoice.objects.select_related("product").iterator():
        amount_sources = ("extra", "replacement", "manual_extra")
        if choice.source not in amount_sources:
            continue

        if choice.applied_vat_rate is not None:
            continue

        if choice.source == "manual_extra":
            choice.applied_vat_rate = menu_rate
        elif choice.product_id:
            choice.applied_vat_rate = product_rates.get(
                choice.product_id,
                menu_rate,
            )
        else:
            choice.applied_vat_rate = menu_rate

        choice.save(update_fields=["applied_vat_rate"])


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0015_payment_guest_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="vat_rate",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("10.00"),
                max_digits=4,
            ),
        ),
        migrations.AddField(
            model_name="guestorder",
            name="menu_applied_vat_rate",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("10.00"),
                max_digits=4,
            ),
        ),
        migrations.AddField(
            model_name="guestchoice",
            name="applied_vat_rate",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=4,
                null=True,
            ),
        ),
        migrations.RunPython(backfill_applied_vat_rates, migrations.RunPython.noop),
    ]
