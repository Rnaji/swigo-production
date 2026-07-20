from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0014_diningorder_wizard_draft"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="guest_number",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
