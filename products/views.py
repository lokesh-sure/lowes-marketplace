from django.shortcuts import render, get_object_or_404

from .models import Product, ProductImage


def product_list(request):

    query = request.GET.get('q')

    products = Product.objects.all()

    if query:
        products = Product.objects.filter(
            name__icontains=query
        )

    return render(
        request,
        'products/product_list.html',
        {
            'products': products
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