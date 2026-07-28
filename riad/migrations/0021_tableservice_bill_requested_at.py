from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0020_kitchenticketitem_serve_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="tableservice",
            name="bill_requested_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Addition demandée à",
            ),
        ),
    ]
