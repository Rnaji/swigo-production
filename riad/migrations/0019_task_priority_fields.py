from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("riad", "0018_tableservice_task_claimed_extra_ticket"),
    ]

    operations = [
        migrations.AddField(
            model_name="kitchenticketitem",
            name="done_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Marqué fait à",
            ),
        ),
        migrations.AddField(
            model_name="tableservice",
            name="task_claimed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="claimed_table_tasks",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Tâche prise en charge par",
            ),
        ),
    ]
