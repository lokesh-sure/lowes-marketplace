from django.urls import path

from .views import (
    order_list,
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
        "place/",
        place_order,
        name="place_order"
    ),

]