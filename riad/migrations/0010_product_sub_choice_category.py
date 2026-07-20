from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0009_alter_payment_options_alter_payment_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="sub_choice_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sub_choice_parents",
                to="riad.productcategory",
                verbose_name="Catégorie de sous-choix",
            ),
        ),
    ]
