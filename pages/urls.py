from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("about/", views.about, name="about"),
    path("privacy/", views.privacy, name="privacy"),
    path("help/", views.help_center, name="help"),
    path("admin-access/", views.admin_access, name="admin_access"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/products/", views.admin_products, name="admin_products"),
    path("admin-dashboard/products/new/", views.admin_product_form, name="admin_product_new"),
    path("admin-dashboard/products/<int:product_id>/edit/", views.admin_product_form, name="admin_product_edit"),
    path("admin-dashboard/products/<int:product_id>/delete/", views.admin_product_delete, name="admin_product_delete"),
    path("admin-dashboard/customers/", views.admin_customers, name="admin_customers"),
    path("admin-dashboard/customers/<int:user_id>/edit/", views.admin_customer_edit, name="admin_customer_edit"),
    path("admin-dashboard/customers/<int:user_id>/toggle/", views.admin_customer_toggle, name="admin_customer_toggle"),
    path("contact/", views.contact, name="contact"),
]
