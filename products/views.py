from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    """商品一覧ページを表示するビュー"""
    products = Product.objects.filter(is_active=True).order_by("id")

    return render(request, "products/product_list.html", {"products": products})

def product_detail(request, pk: int):
    """
    商品詳細ページを表示するビュー。

    - URL から渡された pk に対応する Product を1件取得する
    - 「Related products」として最新の商品をいくつか取得する
    """
    
    product = get_object_or_404(Product, pk=pk, is_active=True)
    # 関連商品を4件表示する
    # 自分自身（pk）が含まれないように除外し、新しい順に4件取得
    related_products = (
        Product.objects.filter(is_active=True)
        .exclude(pk=pk)
        .order_by("-created_at")[:4]
    )

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "products/product_detail.html", context)