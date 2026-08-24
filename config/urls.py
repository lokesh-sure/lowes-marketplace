from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_redirect(request):
    return redirect("products:product_list")


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    # Home
    path(
        "",
        home_redirect,
        name="home"
    ),

    # Products
    path(
        "products/",
        include("products.urls")
    ),

    # Accounts
    path(
        "accounts/",
        include("accounts.urls")
    ),

    # Cart
    path(
        "cart/",
        include("cart.urls")
    ),

    # Wishlist
    path(
        "wishlist/",
        include("wishlist.urls")
    ),

    # Orders
    path(
        "orders/",
        include("orders.urls")
    ),
]


if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )