from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Order, OrderItem
from cart.models import CartItem


@login_required
def order_list(request):
    orders = Order.objects.filter(
        user=request.user
    )

    return render(
        request,
        'orders/order_list.html',
        {
            'orders': orders
        }
    )


@login_required
def place_order(request):

    if request.method == 'POST':

        order = Order.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            address=request.POST['address'],
            city=request.POST['city']
        )

        cart_items = CartItem.objects.filter(
            cart__user=request.user
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        return render(
            request,
            'orders/success.html'
        )

    return render(
        request,
        'orders/place_order.html'
    )