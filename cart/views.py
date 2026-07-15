from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem
from products.models import Product


@login_required
def add_to_cart(request, product_id):

    cart = Cart.objects.get(
        user=request.user
    )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Out-of-stock product cart lo add avvakunda prevent chesthundi
    if product.stock <= 0:

        return redirect(
            'view_cart'
        )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # Product already cart lo unte quantity increase chesthundi
    if not created:

        # Available stock kanna quantity ekkuva avvakunda prevent chesthundi
        if cart_item.quantity < product.stock:

            cart_item.quantity += 1

            cart_item.save(
                update_fields=[
                    'quantity'
                ]
            )

    return redirect(
        'view_cart'
    )


@login_required
def view_cart(request):

    cart = Cart.objects.get(
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart
    ).select_related(
        'product'
    )

    total = 0

    for item in cart_items:

        total += (
            item.product.price
            * item.quantity
        )

    return render(
        request,
        'cart/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )


@login_required
def increase_quantity(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    # Available product stock varake quantity increase avutundi
    if cart_item.quantity < cart_item.product.stock:

        cart_item.quantity += 1

        cart_item.save(
            update_fields=[
                'quantity'
            ]
        )

    return redirect(
        'view_cart'
    )


@login_required
def decrease_quantity(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    # Quantity 1 kanna ekkuva unte decrease chesthundi
    if cart_item.quantity > 1:

        cart_item.quantity -= 1

        cart_item.save(
            update_fields=[
                'quantity'
            ]
        )

    else:

        # Quantity 1 daggara minus click chesthe item remove avutundi
        cart_item.delete()

    return redirect(
        'view_cart'
    )


@login_required
def remove_from_cart(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    cart_item.delete()

    return redirect(
        'view_cart'
    )