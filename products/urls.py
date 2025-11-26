from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # --- 一般ユーザー向け ---
    path("", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),

    # --- 管理者向け ---
    path("manage/products/", views.manage_product_list, name="manage_product_list"),
    path("manage/products/create/", views.manage_product_create, name="manage_product_create"),
    path("manage/products/<int:pk>/edit/", views.manage_product_edit, name="manage_product_edit"),
    path("manage/products/<int:pk>/delete/", views.manage_product_delete, name="manage_product_delete"),
    
    # --- カート関連 ---
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/delete/<int:item_id>/", views.cart_item_delete, name="cart_item_delete"),
]
