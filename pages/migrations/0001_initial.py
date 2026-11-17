# Generated for homepage sale posters.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SalePoster",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image_data", models.BinaryField()),
                ("image_content_type", models.CharField(max_length=32)),
                ("alt_text", models.CharField(default="Store sale poster", max_length=200)),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("position", "id"),
            },
        ),
    ]
