from django.db import models
from django.contrib.staticfiles.storage import staticfiles_storage


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def fallback_image_url(self):
        category_name = self.category.name.lower() if self.category else ""
        product_name = self.name.lower()
        if "appliance" in category_name or "refrigerator" in product_name:
            image_name = "refrigerator.jpg"
        elif "furniture" in category_name or "sofa" in product_name:
            image_name = "sofa.jpg"
        else:
            image_name = "tv.jpg"
        return staticfiles_storage.url(f"images/{image_name}")


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to='products/'
    )

    def __str__(self):
        return self.product.name
