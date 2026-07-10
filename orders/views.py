from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Order, OrderItem
from cart.models import CartItem


@login_required
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by(
        '-created_at'
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

    cart_items = CartItem.objects.filter(
        cart__user=request.user
    )

    if request.method == 'POST':

        # Empty cart tho order create avvakunda prevent chesthundi
        if not cart_items.exists():

            return render(
                request,
                'orders/place_order.html',
                {
                    'error': 'Your cart is empty.'
                }
            )

        # Cart total calculate chesthundi
        total_amount = sum(
            item.product.price * item.quantity
            for item in cart_items
        )

        # Order create chesthundi
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            address=request.POST['address'],
            city=request.POST['city'],
            total_amount=total_amount,
            status='Pending'
        )

        # Cart products ni OrderItem table lo save chesthundi
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        # Order successful ayyaka cart clear chesthundi
        cart_items.delete()

        return render(
            request,
            'orders/success.html',
            {
                'order': order
            }
        )

    return render(
        request,
        'orders/place_order.html',
        {
            'cart_items': cart_items
        }
    )