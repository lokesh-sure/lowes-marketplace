from products.models import Product, Category


products = [
    ("Galaxy Demo Phone X1", "Samsung", "ELECTRONICS", 45999, 20),
    ("Bravia Demo Smart TV", "Sony", "ELECTRONICS", 64999, 15),
    ("OLED Demo TV 55", "LG", "ELECTRONICS", 72999, 12),
    ("Bluetooth Demo Speaker", "Sony", "ELECTRONICS", 8999, 25),
    ("Wireless Demo Headphones", "JBL", "ELECTRONICS", 5999, 30),

    ("Frost Free Demo Refrigerator", "LG", "APPLIANCES", 48999, 10),
    ("Double Door Demo Refrigerator", "Samsung", "APPLIANCES", 55999, 10),
    ("Demo Washing Machine 7KG", "Whirlpool", "APPLIANCES", 32999, 12),
    ("Demo Air Conditioner 1.5T", "Voltas", "APPLIANCES", 41999, 8),
    ("Demo Mixer Grinder", "Bajaj", "APPLIANCES", 4999, 20),

    ("Demo Smartphone Pro", "Apple", "MOBILES & COMPUTERS", 79999, 10),
    ("Demo Smartphone A1", "OnePlus", "MOBILES & COMPUTERS", 39999, 15),
    ("Demo Laptop 14", "HP", "MOBILES & COMPUTERS", 62999, 10),
    ("Demo Laptop Pro", "Dell", "MOBILES & COMPUTERS", 74999, 8),
    ("Demo Gaming Laptop", "Lenovo", "MOBILES & COMPUTERS", 89999, 6),

    ("Demo Office Chair", "Wakefit", "FURNITURE", 8999, 20),
    ("Demo Study Table", "Urban Ladder", "FURNITURE", 12999, 15),
    ("Demo King Bed", "Wakefit", "FURNITURE", 29999, 8),
    ("Demo Bookshelf", "Urban Ladder", "FURNITURE", 9999, 12),
    ("Demo Sofa Set", "Pepperfry", "FURNITURE", 34999, 7),

    ("Demo Air Fryer", "Philips", "HOME & KITCHEN", 8999, 15),
    ("Demo Electric Kettle", "Prestige", "HOME & KITCHEN", 1999, 25),
    ("Demo Induction Cooktop", "Prestige", "HOME & KITCHEN", 2999, 20),
    ("Demo Coffee Maker", "Philips", "HOME & KITCHEN", 6999, 12),
    ("Demo Dinner Set", "Milton", "HOME & KITCHEN", 2499, 25),

    ("Demo Running Shoes", "Nike", "FASHION", 7999, 20),
    ("Demo Sports Shoes", "Adidas", "FASHION", 6999, 20),
    ("Demo Casual Sneakers", "Puma", "FASHION", 4999, 25),
    ("Demo Hoodie", "Adidas", "FASHION", 2999, 30),
    ("Demo Backpack", "Puma", "FASHION", 2499, 25),

    ("Demo Face Wash", "Nivea", "BEAUTY & PERSONAL CARE", 499, 40),
    ("Demo Moisturizer", "Nivea", "BEAUTY & PERSONAL CARE", 699, 35),
    ("Demo Hair Dryer", "Philips", "BEAUTY & PERSONAL CARE", 2499, 20),
    ("Demo Electric Trimmer", "Philips", "BEAUTY & PERSONAL CARE", 1999, 25),
    ("Demo Grooming Kit", "Philips", "BEAUTY & PERSONAL CARE", 3999, 15),

    ("Demo Football", "Adidas", "SPORTS & FITNESS", 1999, 20),
    ("Demo Cricket Bat", "SS", "SPORTS & FITNESS", 4999, 12),
    ("Demo Yoga Mat", "Decathlon", "SPORTS & FITNESS", 999, 30),
    ("Demo Dumbbell Set", "Decathlon", "SPORTS & FITNESS", 2999, 20),
    ("Demo Fitness Cycle", "Decathlon", "SPORTS & FITNESS", 14999, 8),
]


created = 0
existing = 0

for name, brand, category_name, price, stock in products:

    category = Category.objects.get(name=category_name)

    product, was_created = Product.objects.get_or_create(
        name=name,
        brand=brand,
        defaults={
            "category": category,
            "price": price,
            "description": f"{brand} {name} - MarketNest demo product.",
            "stock": stock,
        },
    )

    if was_created:
        created += 1
    else:
        existing += 1


print(f"Products created: {created}")
print(f"Products already existing: {existing}")
print(f"Total products in database: {Product.objects.count()}")