from django.contrib import admin

from .models import (
    Category,
    Product,
    ProductImage
)


class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'brand',
        'price',
        'stock',
        'category'
    )

    list_filter = (
        'category',
        'brand'
    )

    search_fields = (
        'name',
        'brand'
    )

    inlines = [
        ProductImageInline
    ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name'
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'product'
    )