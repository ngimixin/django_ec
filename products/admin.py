from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sku",
        "name",
        "price",
        "stock",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "sku")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "postal_code",
        "total_amount",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "email", "phone", "postal_code", "address")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "price",
        "quantity",
        "created_at",
        "updated_at",
    )
    search_fields = ("order__name", "product__name")
