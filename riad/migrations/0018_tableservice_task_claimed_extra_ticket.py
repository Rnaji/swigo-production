from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0017_tableservice_task_claimed_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="tableservice",
            name="task_claimed_extra_ticket",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="claimed_server_tasks",
                to="riad.kitchenticket",
                verbose_name="Bon extra pris en charge",
            ),
        ),
    ]
