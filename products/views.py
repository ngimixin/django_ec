from django.shortcuts import render
from django.http import HttpResponse
from .models import Product


def product_list(request):
    """商品一覧ページを表示するビュー"""
    products = Product.objects.all().filter(is_active=True).order_by("id")

    return render(request, "products/product_list.html", {"products": products})
