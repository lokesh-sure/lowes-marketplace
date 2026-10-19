from django.urls import path

from .views import (
    order_list,
    order_detail,
    place_order,
    verify_payment,
    order_success,
)

app_name = "orders"

urlpatterns = [

    path(
        "success/",
        order_success,
        name="success"
    ),

    path(
        "",
        order_list,
        name="order_list"
    ),

    path(
        "<int:pk>/",
        order_detail,
        name="order_detail"
    ),

    path(
        "place/",
        place_order,
        name="place_order"
    ),

    path(
        "verify-payment/",
        verify_payment,
        name="verify_payment"
    ),

]
