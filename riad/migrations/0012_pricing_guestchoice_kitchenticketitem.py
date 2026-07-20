from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0011_product_short_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="guestchoice",
            name="label",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="guestchoice",
            name="line_total",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=8, null=True
            ),
        ),
        migrations.AddField(
            model_name="guestchoice",
            name="replaced_product_name",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="guestchoice",
            name="station",
            field=models.CharField(
                blank=True,
                choices=[("kitchen", "Cuisine"), ("bar", "Bar / Office")],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="guestchoice",
            name="supplement_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name="guestchoice",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.PROTECT,
                related_name="guest_choices",
                to="riad.product",
            ),
        ),
        migrations.AlterField(
            model_name="guestchoice",
            name="source",
            field=models.CharField(
                choices=[
                    ("menu", "Menu"),
                    ("extra", "Supplément"),
                    ("replacement", "Remplacement"),
                    ("manual_extra", "Supplément libre"),
                    ("offered", "Offert"),
                ],
                default="menu",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="kitchenticketitem",
            name="label",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AlterField(
            model_name="kitchenticketitem",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.PROTECT,
                to="riad.product",
            ),
        ),
        migrations.AlterField(
            model_name="kitchenticketitem",
            name="section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.PROTECT,
                to="riad.menusection",
            ),
        ),
    ]
