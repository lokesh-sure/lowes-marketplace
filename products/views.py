from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product, ProductImage, Category


def product_list(request):

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category")
    brand = request.GET.get("brand", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    products = Product.objects.all().select_related("category")
    categories = Category.objects.all().order_by("name")

    brands = (
        Product.objects
        .values_list("brand", flat=True)
        .distinct()
        .order_by("brand")
    )

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    if brand:
        products = products.filter(
            brand__iexact=brand
        )

    if min_price:
        try:
            products = products.filter(
                price__gte=float(min_price)
            )
        except ValueError:
            min_price = ""

    if max_price:
        try:
            products = products.filter(
                price__lte=float(max_price)
            )
        except ValueError:
            max_price = ""

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "categories": categories,
            "brands": brands,
            "query": query,
            "selected_category": category_id,
            "selected_brand": brand,
            "min_price": min_price,
            "max_price": max_price,
        }
    )


def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    product_images = ProductImage.objects.filter(
        product=product
    )

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    )[:4]

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "product_images": product_images,
            "related_products": related_products
        }
    )