from django.shortcuts import get_object_or_404, redirect, render
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

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.get(user=request.user)

    cart_items = CartItem.objects.filter(
        cart=cart
    )

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render(
        request,
        'cart/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id
    )

    cart_item.delete()

    return redirect('view_cart')