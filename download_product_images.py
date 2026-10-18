
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Download suitable category images into Django's media folder.
# This script does not modify the database or existing image records.

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "media" / "products" / "catalog"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# Unsplash Source image URLs are not guaranteed to be stable.
# Test each URL and save only valid image responses.
IMAGES = {
    "smartphone.jpg": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80",
    "television.jpg": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=800&q=80",
    "headphones.jpg": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
    "laptop.jpg": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
    "furniture.jpg": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80",
    "shoes.jpg": "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80",
    "backpack.jpg": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80",
    "skincare.jpg": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80",
    "fitness.jpg": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=800&q=80",
    "kitchen.jpg": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80",
}

for filename, url in IMAGES.items():
    destination = IMAGE_DIR / filename

    if destination.exists():
        print(f"SKIP (already exists): {filename}")
        continue

    try:
        request = Request(
            url,
            headers={"User-Agent": "MarketNestCatalogImageSetup/1.0"},
        )

        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")

            if response.status != 200 or not content_type.startswith("image/"):
                print(f"SKIP (not an image): {filename} [{content_type}]")
                continue

            data = response.read()

        if not data:
            print(f"SKIP (empty response): {filename}")
            continue

        destination.write_bytes(data)
        print(f"DOWNLOADED: {filename} ({len(data)} bytes)")

    except (URLError, HTTPError, TimeoutError, OSError) as error:
        print(f"FAILED: {filename} - {error}")

print(f"\nFinished. Images folder: {IMAGE_DIR}")
print("No database records were changed.")
