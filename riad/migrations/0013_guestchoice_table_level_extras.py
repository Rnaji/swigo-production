import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0012_pricing_guestchoice_kitchenticketitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="guestchoice",
            name="order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="table_level_choices",
                to="riad.diningorder",
            ),
        ),
        migrations.AlterField(
            model_name="guestchoice",
            name="guest",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="choices",
                to="riad.guestorder",
            ),
        ),
    ]
