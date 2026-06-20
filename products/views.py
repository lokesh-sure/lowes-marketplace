from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Product


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