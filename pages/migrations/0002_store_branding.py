from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pages", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="StoreBranding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("logo_data", models.BinaryField(blank=True, null=True)),
                ("logo_content_type", models.CharField(blank=True, max_length=32)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
