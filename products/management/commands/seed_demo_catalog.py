from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from products.models import Category, Product


class Command(BaseCommand):
    help = "Create the small, non-customer demo catalog for the public preview site."

    def handle(self, *args, **options):
        if not settings.MARKETNEST_DEMO_MODE:
            raise CommandError("Enable MARKETNEST_DEMO_MODE before seeding preview products.")

        catalog = [
            {
                "name": "Samsung Refrigerator",
                "brand": "Samsung",
                "category": "APPLIANCES",
                "price": "45999.00",
                "stock": 20,
                "description": "Samsung refrigerator from the MarketNest storefront preview.",
            },
            {
                "name": "LG Smart TV",
                "brand": "LG",
                "category": "ELECTRONICS",
                "price": "35999.00",
                "stock": 15,
                "description": "LG smart TV from the MarketNest storefront preview.",
            },
            {
                "name": "Sofa Set",
                "brand": "HomeStyle",
                "category": "FURNITURE",
                "price": "25999.00",
                "stock": 7,
                "description": "Sofa set from the MarketNest storefront preview.",
            },
        ]

        created = 0
        for item in catalog:
            category, _ = Category.objects.get_or_create(name=item["category"])
            product, was_created = Product.objects.get_or_create(
                name=item["name"],
                brand=item["brand"],
                defaults={
                    "category": category,
                    "price": item["price"],
                    "stock": item["stock"],
                    "description": item["description"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Preview catalog ready ({created} new products)."))
