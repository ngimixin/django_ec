from typing import Any

from django.contrib import admin
from django.http import HttpRequest

from .models import Product, Order, OrderItem, PromotionCode


def get_app_list(
    self: admin.AdminSite, request: HttpRequest, app_label: str | None = None
) -> list[dict[str, Any]]:
    """管理画面サイドバーのモデル並び順をカスタマイズする。"""
    app_dict = self._build_app_dict(request, app_label)

    # モデルの希望順序を定義
    model_order = ["Product", "PromotionCode", "Order", "OrderItem"]

    for app_name, app in app_dict.items():
        if app_name == "products":
            app["models"].sort(
                key=lambda x: (
                    model_order.index(x["object_name"])
                    if x["object_name"] in model_order
                    else 999
                )
            )

    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
    return app_list


admin.AdminSite.get_app_list = get_app_list


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


@admin.register(PromotionCode)
class PromotionCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_amount",
        "is_used",
        "used_at",
        "created_at",
    )
    list_filter = ("is_used",)
    search_fields = ("code",)
