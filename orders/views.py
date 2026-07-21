from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Order, OrderItem
from cart.models import CartItem


@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders
        }
    )


@login_required
def place_order(request):

    cart_items = CartItem.objects.filter(
        cart__user=request.user
    ).select_related("product")

    if request.method == "POST":

        if not cart_items.exists():

            return render(
                request,
                "orders/place_order.html",
                {
                    "cart_items": cart_items,
                    "error": "Your cart is empty."
                }
            )

        for item in cart_items:

            if item.product.stock < item.quantity:

                return render(
                    request,
                    "orders/place_order.html",
                    {
                        "cart_items": cart_items,
                        "error": f"Only {item.product.stock} item(s) available for {item.product.name}."
                    }
                )

        with transaction.atomic():

            total_amount = sum(
                item.product.price * item.quantity
                for item in cart_items
            )

            order = Order.objects.create(
                user=request.user,
                full_name=request.POST.get("full_name"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                total_amount=total_amount,
                status="Pending",
            )

            for item in cart_items:

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

                item.product.stock -= item.quantity
                item.product.save(update_fields=["stock"])

            cart_items.delete()

        return render(
            request,
            "orders/success.html",
            {
                "order": order
            }
        )

    return render(
        request,
        "orders/place_order.html",
        {
            "cart_items": cart_items
        }
    )