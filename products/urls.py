from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # トップページ（商品一覧）
    path("", views.product_list, name="product_list"),
    # 商品詳細（/products/<pk>/）
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
]
