from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product, ProductImage, Category


def product_list(request):

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query)
        )

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'categories': categories,
            'query': query,
            'selected_category': category_id,
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
        'products/product_detail.html',
        {
            'product': product,
            'product_images': product_images,
            'related_products': related_products
        }
    )