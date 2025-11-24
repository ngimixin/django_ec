from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request: HttpRequest) -> HttpResponse:
    """公開中の商品一覧ページを表示する。"""
    products = Product.objects.filter(is_active=True).order_by("-created_at")

    return render(request, "products/product_list.html", {"products": products})


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """商品詳細ページを表示するビュー。

    URL の pk から対象の商品を取得し、関連商品として他の最新4件の商品も
    あわせてテンプレートに渡して表示する。
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)

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
