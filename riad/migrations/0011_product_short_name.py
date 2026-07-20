from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riad", "0010_product_sub_choice_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="short_name",
            field=models.CharField(
                blank=True,
                help_text="Libellé court pour l'affichage dans le wizard.",
                max_length=80,
                verbose_name="Nom court",
            ),
        ),
    ]
