from django.urls import path

from .views import (
    order_list,
    order_detail,
    place_order,
)

app_name = "orders"

urlpatterns = [

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

]