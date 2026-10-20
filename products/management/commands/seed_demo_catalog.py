import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from products.models import Category, Product, ProductImage


class Command(BaseCommand):
    help = "Load the public storefront catalog fixture for the preview site."

    def handle(self, *args, **options):
        if not settings.MARKETNEST_DEMO_MODE:
            raise CommandError("Enable MARKETNEST_DEMO_MODE before seeding preview products.")

        fixture = Path(settings.BASE_DIR) / "static" / "demo_catalog.json"
        if not fixture.is_file():
            raise CommandError(f"Demo catalog fixture not found: {fixture}")

        rows = json.loads(fixture.read_text(encoding="utf-8"))
        categories_by_id = {}
        for row in rows:
            if row["model"] == "products.category":
                category, _ = Category.objects.get_or_create(name=row["fields"]["name"])
                categories_by_id[row["pk"]] = category

        products_by_id = {}
        for row in rows:
            if row["model"] != "products.product":
                continue
            fields = row["fields"]
            product, _ = Product.objects.update_or_create(
                pk=row["pk"],
                defaults={
                    "name": fields["name"],
                    "brand": fields["brand"],
                    "category": categories_by_id.get(fields.get("category")),
                    "price": fields["price"],
                    "description": fields["description"],
                    "stock": fields["stock"],
                },
            )
            products_by_id[row["pk"]] = product

        image_count = 0
        for row in rows:
            if row["model"] != "products.productimage":
                continue
            fields = row["fields"]
            _, created = ProductImage.objects.get_or_create(
                product=products_by_id[fields["product"]],
                image=fields["image"],
            )
            image_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Preview catalog ready ({len(products_by_id)} products, {image_count} new image references)."
            )
        )
