from decimal import Decimal

import razorpay

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

from .models import Order, OrderItem, Payment
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
def order_detail(request, pk):

    order = Order.objects.filter(
        id=pk,
        user=request.user
    ).prefetch_related(
        "items__product",
        "payments"
    ).first()

    if not order:
        return render(
            request,
            "orders/order_detail.html",
            {
                "error": "Order not found."
            },
            status=404
        )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order
        }
    )


@login_required
def place_order(request):

    cart_items = CartItem.objects.filter(
        cart__user=request.user
    ).select_related("product")

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
                    "error": (
                        f"Only {item.product.stock} item(s) available "
                        f"for {item.product.name}."
                    )
                }
            )

    total_amount = sum(
        (
            item.product.price * item.quantity
            for item in cart_items
        ),
        Decimal("0.00")
    )

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()

        if not full_name or not address or not city:

            return render(
                request,
                "orders/place_order.html",
                {
                    "cart_items": cart_items,
                    "error": "Please fill in all delivery details."
                }
            )

        try:

            razorpay_client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            razorpay_order = razorpay_client.order.create(
                {
                    "amount": int(total_amount * 100),
                    "currency": "INR",
                    "receipt": f"marketnest_{request.user.id}_{request.session.session_key or 'new'}",
                }
            )

        except Exception:

            return render(
                request,
                "orders/place_order.html",
                {
                    "cart_items": cart_items,
                    "error": (
                        "Unable to start payment. "
                        "Please try again."
                    )
                },
                status=500
            )

        request.session["checkout_data"] = {
            "full_name": full_name,
            "address": address,
            "city": city,
        }

        request.session["checkout_cart_total"] = str(total_amount)

        return render(
            request,
            "orders/place_order.html",
            {
                "cart_items": cart_items,
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "razorpay_amount": int(total_amount * 100),
                "full_name": full_name,
                "address": address,
                "city": city,
            }
        )

    return render(
        request,
        "orders/place_order.html",
        {
            "cart_items": cart_items,
            "total_amount": total_amount,
        }
    )


@login_required
def verify_payment(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request method."
            },
            status=405
        )

    return JsonResponse(
        {
            "success": False,
            "error": "Payment verification is not implemented yet."
        },
        status=501
    )