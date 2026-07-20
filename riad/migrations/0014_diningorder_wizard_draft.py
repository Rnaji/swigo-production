from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0013_guestchoice_table_level_extras"),
    ]

    operations = [
        migrations.AddField(
            model_name="diningorder",
            name="wizard_draft",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
