from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem
from products.models import Product


@login_required
def add_to_cart(request, product_id):
    cart = Cart.objects.get(user=request.user)

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('admin:index')