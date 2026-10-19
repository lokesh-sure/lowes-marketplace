
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import home_view
from pages.views import addresses


urlpatterns = [
    path("admin/", admin.site.urls),

    # MarketNest Homepage
    path("", home_view, name="home"),

    # Products
    path("products/", include("products.urls")),

    # Accounts
    path("accounts/", include("accounts.urls")),

    # Cart
    path("cart/", include("cart.urls")),

    # Wishlist
    path("wishlist/", include("wishlist.urls")),

    # Orders
    path("orders/", include("orders.urls")),

    # Original storefront information pages
    path("pages/", include("pages.urls")),
    path("addresses/", addresses, name="saved_addresses"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
