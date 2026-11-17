from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_productimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="image_data",
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="category",
            name="image_content_type",
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
