from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "brand",
        "price",
        "stock",
        "category",
    )

    list_filter = (
        "category",
        "brand",
    )

    search_fields = (
        "name",
        "brand",
        "description",
    )

    list_editable = (
        "price",
        "stock",
    )

    inlines = [
        ProductImageInline,
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "image",
    )

    search_fields = (
        "product__name",
    )