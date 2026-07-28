from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0016_vat_rates"),
    ]

    operations = [
        migrations.AddField(
            model_name="tableservice",
            name="task_claimed_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Tâche prise en charge à",
            ),
        ),
    ]
