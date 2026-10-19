import hashlib
import hmac
from decimal import Decimal

import razorpay

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages

from .models import Order, OrderItem, Payment
from cart.models import CartItem


@login_required
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")
    search_query = request.GET.get("q", "").strip()
    if search_query:
        if search_query.isdigit():
            orders = orders.filter(id=int(search_query))
        else:
            orders = orders.filter(
                Q(full_name__icontains=search_query)
                | Q(city__icontains=search_query)
                | Q(status__icontains=search_query)
            )

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders,
            "search_query": search_query,
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
def order_success(request):
    order_id = request.session.get("last_order_id")
    if not order_id:
        messages.error(request, "There is no completed order to show yet.")
        return redirect("orders:order_list")

    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/success.html", {"order": order})


@login_required
def place_order(request):
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related("product")
    if not cart_items.exists():
        return render(request, "orders/place_order.html", {
            "cart_items": cart_items,
            "total_amount": Decimal("0.00"),
            "error": "Your cart is empty.",
        })

    for item in cart_items:
        if item.product.stock < item.quantity:
            return render(request, "orders/place_order.html", {
                "cart_items": cart_items,
                "total_amount": Decimal("0.00"),
                "error": f"Only {item.product.stock} item(s) available for {item.product.name}.",
            })

    total_amount = sum(
        (item.product.price * item.quantity for item in cart_items),
        Decimal("0.00"),
    )

    if request.method == "POST":
        form_data = {
            "full_name": request.POST.get("full_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "pincode": request.POST.get("pincode", "").strip(),
            "payment": request.POST.get("payment", "upi").strip().lower(),
        }
        if not all(form_data[key] for key in ("full_name", "phone", "address", "city", "pincode")):
            return render(request, "orders/place_order.html", {
                "cart_items": cart_items,
                "total_amount": total_amount,
                "error": "Please fill in all delivery details.",
                **form_data,
            })
        if form_data["payment"] not in {"upi", "card", "cod"}:
            return render(request, "orders/place_order.html", {
                "cart_items": cart_items,
                "total_amount": total_amount,
                "error": "Please choose a valid payment method.",
                **form_data,
            })

        checkout_data = {
            "full_name": form_data["full_name"],
            "address": (
                f"{form_data['address']}\n"
                f"PIN Code: {form_data['pincode']}\n"
                f"Mobile: {form_data['phone']}"
            ),
            "city": form_data["city"],
        }

        if form_data["payment"] == "cod":
            order, error = _create_order_from_cart(request, total_amount, checkout_data)
            if error:
                return render(request, "orders/place_order.html", {
                    "cart_items": CartItem.objects.filter(cart__user=request.user).select_related("product"),
                    "total_amount": total_amount,
                    "error": error,
                    **form_data,
                })
            return redirect("orders:success")

        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            return render(request, "orders/place_order.html", {
                "cart_items": cart_items,
                "total_amount": total_amount,
                "error": "Online payment is not configured. Choose Cash on Delivery or contact support.",
                **form_data,
            }, status=503)

        try:
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = razorpay_client.order.create({
                "amount": int(total_amount * 100),
                "currency": "INR",
                "receipt": f"marketnest_{request.user.id}_{request.session.session_key or 'new'}",
            })
        except Exception:
            return render(request, "orders/place_order.html", {
                "cart_items": cart_items,
                "total_amount": total_amount,
                "error": "Unable to start payment. Please try again.",
                **form_data,
            }, status=502)

        request.session["checkout_data"] = checkout_data
        request.session["checkout_cart_total"] = str(total_amount)
        request.session["razorpay_order_id"] = razorpay_order["id"]
        return render(request, "orders/place_order.html", {
            "cart_items": cart_items,
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_amount": int(total_amount * 100),
            "total_amount": total_amount,
            **form_data,
        })

    return render(request, "orders/place_order.html", {
        "cart_items": cart_items,
        "total_amount": total_amount,
    })


def _create_order_from_cart(request, expected_total, checkout_data, is_paid=False, payment_data=None):
    with transaction.atomic():
        locked_items = list(
            CartItem.objects.select_for_update()
            .filter(cart__user=request.user)
            .select_related("product")
        )
        if not locked_items:
            return None, "Your cart is empty."

        for item in locked_items:
            if item.product.stock < item.quantity:
                return None, f"Only {item.product.stock} item(s) remain for {item.product.name}."

        current_total = sum(
            (item.product.price * item.quantity for item in locked_items),
            Decimal("0.00"),
        )
        if current_total != expected_total:
            return None, "The cart total changed. Please review checkout again."

        order = Order.objects.create(
            user=request.user,
            full_name=checkout_data["full_name"],
            address=checkout_data["address"],
            city=checkout_data["city"],
            total_amount=current_total,
            is_paid=is_paid,
            status="Confirmed" if is_paid else "Pending",
        )
        OrderItem.objects.bulk_create([
            OrderItem(order=order, product=item.product, quantity=item.quantity)
            for item in locked_items
        ])
        for item in locked_items:
            item.product.stock -= item.quantity
            item.product.save(update_fields=["stock"])
        CartItem.objects.filter(id__in=[item.id for item in locked_items]).delete()

        if payment_data:
            Payment.objects.create(order=order, amount=current_total, **payment_data)

    request.session["last_order_id"] = order.id
    return order, None


@login_required
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    razorpay_order_id = request.POST.get("razorpay_order_id", "")
    razorpay_payment_id = request.POST.get("razorpay_payment_id", "")
    razorpay_signature = request.POST.get("razorpay_signature", "")
    expected_order_id = request.session.get("razorpay_order_id")
    checkout_data = request.session.get("checkout_data")
    checkout_total = request.session.get("checkout_cart_total")
    secret = settings.RAZORPAY_KEY_SECRET

    if not all((razorpay_order_id, razorpay_payment_id, razorpay_signature,
                expected_order_id, checkout_data, checkout_total, secret)):
        return JsonResponse({"success": False, "error": "Checkout session is missing or expired. Please try again."}, status=400)
    if not hmac.compare_digest(razorpay_order_id, expected_order_id):
        return JsonResponse({"success": False, "error": "Payment order does not match this checkout."}, status=400)

    signed_payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
    expected_signature = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(razorpay_signature, expected_signature):
        return JsonResponse({"success": False, "error": "Payment signature could not be verified."}, status=400)

    existing_payment = Payment.objects.filter(
        razorpay_order_id=razorpay_order_id, order__user=request.user
    ).select_related("order").first()
    if existing_payment:
        request.session["last_order_id"] = existing_payment.order_id
        return JsonResponse({"success": True, "redirect_url": reverse("orders:success")})

    try:
        total_amount = Decimal(checkout_total)
    except Exception:
        return JsonResponse({"success": False, "error": "Checkout total is invalid."}, status=400)

    payment_data = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
        "status": "Paid",
    }
    order, error = _create_order_from_cart(
        request, total_amount, checkout_data, is_paid=True, payment_data=payment_data
    )
    if error:
        return JsonResponse({"success": False, "error": error}, status=409)

    request.session.pop("checkout_data", None)
    request.session.pop("checkout_cart_total", None)
    request.session.pop("razorpay_order_id", None)
    return JsonResponse({"success": True, "redirect_url": reverse("orders:success")})
