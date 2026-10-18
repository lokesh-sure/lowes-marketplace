
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import transaction

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from products.models import Product, ProductImage


BASE_DIR = Path(__file__).resolve().parent
CATALOG_DIR = BASE_DIR / "media" / "products" / "catalog"

# Category-based placeholder images.
# These are generic category photos, not exact brand/model photos.
IMAGE_RULES = [
    (("phone", "smartphone", "galaxy"), "smartphone.jpg"),
    (("tv", "television", "bravia", "oled"), "television.jpg"),
    (("headphone", "speaker", "audio"), "headphones.jpg"),
    (("laptop", "computer", "notebook"), "laptop.jpg"),
    (("chair", "table", "bed", "sofa", "bookshelf", "furniture"), "furniture.jpg"),
    (("shoe", "sneaker", "running"), "shoes.jpg"),
    (("backpack", "bag"), "backpack.jpg"),
    (("face wash", "moisturizer", "skincare", "cream"), "skincare.jpg"),
    (("football", "cricket", "yoga", "dumbbell", "fitness", "cycle"), "fitness.jpg"),
    (("refrigerator", "refregirator", "washing machine", "air conditioner",
      "mixer", "kettle", "cooktop", "coffee maker", "dinner set",
      "air fryer", "dryer", "trimmer", "grooming"), "kitchen.jpg"),
]


def choose_image(product):
    text = f"{product.name} {product.brand}".lower()

    for keywords, filename in IMAGE_RULES:
        if any(keyword in text for keyword in keywords):
            return CATALOG_DIR / filename

    return None


def main():
    if not CATALOG_DIR.exists():
        print(f"Image folder not found: {CATALOG_DIR}")
        return

    added = 0
    skipped_existing = 0
    skipped_missing = 0
    unmatched = 0

    with transaction.atomic():
        for product in Product.objects.all().order_by("id"):
            if ProductImage.objects.filter(product=product).exists():
                skipped_existing += 1
                print(f"KEEP existing image: {product.id} - {product.name}")
                continue

            image_path = choose_image(product)

            if image_path is None:
                unmatched += 1
                print(f"NO CATEGORY MATCH: {product.id} - {product.name}")
                continue

            if not image_path.is_file():
                skipped_missing += 1
                print(f"FILE MISSING: {image_path.name}")
                continue

            with image_path.open("rb") as image_file:
                ProductImage.objects.create(
                    product=product,
                    image=File(image_file, name=image_path.name),
                )

            added += 1
            print(f"ADDED: {product.id} - {product.name} -> {image_path.name}")

    print("\nImage mapping complete.")
    print(f"New image records: {added}")
    print(f"Products kept unchanged: {skipped_existing}")
    print(f"Missing image files: {skipped_missing}")
    print(f"Products without a category match: {unmatched}")


if __name__ == "__main__":
    main()
