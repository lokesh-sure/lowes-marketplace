from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Wishlist
from products.models import Product
from cart.models import Cart


@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(
        'product_detail',
        product_id=product.id
    )


@login_required
def remove_from_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect('wishlist')


@login_required
def wishlist(request):

    items = Wishlist.objects.filter(
        user=request.user
    )

    return render(
        request,
        'wishlist/wishlist.html',
        {
            'items': items
        }
    )


@login_required
def move_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={
            'quantity': 1
        }
    )

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect('cart')