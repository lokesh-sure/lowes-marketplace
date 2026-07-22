from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem
from products.models import Product


@login_required
def add_to_cart(request, product_id):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product.stock <= 0:
        return redirect("cart:view_cart")

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1
            cart_item.save(update_fields=["quantity"])

    return redirect("cart:view_cart")


@login_required
def view_cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = CartItem.objects.filter(
        cart=cart
    ).select_related("product")

    total = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


@login_required
def increase_quantity(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if cart_item.quantity < cart_item.product.stock:

        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    return redirect("cart:view_cart")


@login_required
def decrease_quantity(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save(update_fields=["quantity"])

    else:

        cart_item.delete()

    return redirect("cart:view_cart")


@login_required
def remove_from_cart(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    cart_item.delete()

    return redirect("cart:view_cart")