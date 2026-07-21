from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Wishlist
from products.models import Product
from cart.models import Cart, CartItem


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
        "products:product_detail",
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

    return redirect("wishlist:wishlist")


@login_required
def wishlist(request):

    items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "items": items
        }
    )


@login_required
def move_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created and cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save(update_fields=["quantity"])

    Wishlist.objects.filter(
        user=request.user,
        product=product
    ).delete()

    return redirect("cart:view_cart")