import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("riad", "0019_task_priority_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="kitchenticketitem",
            name="is_served",
            field=models.BooleanField(default=False, verbose_name="Servi"),
        ),
        migrations.AddField(
            model_name="kitchenticketitem",
            name="served_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Servi à"),
        ),
        migrations.AddField(
            model_name="kitchenticketitem",
            name="serve_batch_id",
            field=models.UUIDField(blank=True, db_index=True, null=True, verbose_name="Lot de service"),
        ),
        migrations.AddField(
            model_name="kitchenticketitem",
            name="serve_claimed_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Pris en charge à"),
        ),
        migrations.AddField(
            model_name="kitchenticketitem",
            name="serve_claimed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="claimed_kitchen_items",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Pris en charge par",
            ),
        ),
    ]
