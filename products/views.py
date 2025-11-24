from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from config.decorators import basic_auth_required as auth
from .forms import ProductForm


def product_list(request: HttpRequest) -> HttpResponse:
    """公開中の商品一覧ページを表示するビュー。"""
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


@auth
def manage_product_list(request: HttpRequest) -> HttpResponse:
    """
    商品管理画面（一覧）を表示するビュー。

    - Product を新しい順に全部取得する
    - manage_product_list.html に渡してテーブルで一覧表示する
    """
    products = Product.objects.all().order_by("-id")
    context = {
        "products": products,
    }
    return render(request, "products/manage_product_list.html", context)


@auth
def manage_product_create(request: HttpRequest) -> HttpResponse:
    """
    商品管理画面：商品を新規作成するビュー。

    - GET: 空のフォームを表示
    - POST: 入力値をバリデーションして Product を作成し、一覧へリダイレクト
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("products:manage_product_list")
    else:
        # 初回アクセス時（GET）は空のフォームを表示
        form = ProductForm()

    context = {
        "form": form,
    }
    return render(request, "products/manage_product_create.html", context)


@auth
def manage_product_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """
    商品管理画面：商品を編集するビュー。

    Args:
        request: HTTPリクエストオブジェクト。
        pk: 編集対象となる Product の主キー。

    Returns:
        編集フォームを表示するHTMLレスポンス、または更新後の商品一覧ページへのリダイレクト。

    Notes:
        - GET の場合は指定した Product の情報を初期値として持つフォームを表示する。
        - POST の場合はフォーム入力内容をバリデーションし、問題なければ既存の Product インスタンスを更新する。
        - 更新後は管理用の商品一覧ページへリダイレクトする。
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("products:manage_product_list")
    else:
        form = ProductForm(instance=product)

    context = {
        "form": form,
        "product": product,
    }

    return render(request, "products/manage_product_edit.html", context)


@auth
def manage_product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    return HttpResponse("商品管理：削除（TODO） - pk={pk}")
