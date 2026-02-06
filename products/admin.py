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
        "promotion_code",
        "promotion_discount_amount",
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "email", "phone", "postal_code", "address")
    readonly_fields = (
        "total_amount",
        "promotion_discount_amount",
        "card_number",
        "card_expire",
        "card_cvv",
        "card_holder",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "注文情報",
            {
                "fields": (
                    "status",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "購入者情報",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "配送先",
            {
                "fields": (
                    "postal_code",
                    "address",
                )
            },
        ),
        (
            "支払い情報（学習用）",
            {
                "fields": (
                    "card_number",
                    "card_expire",
                    "card_cvv",
                    "card_holder",
                )
            },
        ),
        (
            "金額・割引",
            {
                "fields": (
                    "total_amount",
                    "promotion_code",
                    "promotion_discount_amount",
                )
            },
        ),
    )
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
