from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # --- 一般ユーザー向け ---
    path("", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    # --- 管理者向け ---
    path("manage/products/", views.manage_product_list, name="manage_product_list"),
    path(
        "manage/products/create/",
        views.manage_product_create,
        name="manage_product_create",
    ),
    path(
        "manage/products/<int:pk>/edit/",
        views.manage_product_edit,
        name="manage_product_edit",
    ),
    path(
        "manage/products/<int:pk>/delete/",
        views.manage_product_delete,
        name="manage_product_delete",
    ),
    path("manage/orders/", views.manage_order_list, name="manage_order_list"),
    path(
        "manage/orders/<int:pk>/",
        views.manage_order_detail,
        name="manage_order_detail",
    ),
    # --- カート関連 ---
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.cart_item_update, name="cart_item_update"),
    path("cart/delete/<int:item_id>/", views.cart_item_delete, name="cart_item_delete"),
    path(
        "cart/promotion/apply/",
        views.cart_promotion_apply,
        name="cart_promotion_apply",
    ),
    path(
        "cart/promotion/remove/",
        views.cart_promotion_remove,
        name="cart_promotion_remove",
    ),
    # --- 注文関連 ---
    path("order/create/", views.order_create, name="order_create"),
    path("order/complete/", views.order_complete, name="order_complete"),
]
