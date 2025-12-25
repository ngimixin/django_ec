from django.http import JsonResponse, HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from products.services.cart import get_or_create_cart

from .models import Product, Cart, CartItem
from config.decorators import basic_auth_required as auth
from .forms import ProductForm
from .utils import get_quantity_range


def product_list(request: HttpRequest) -> HttpResponse:
    """公開中の商品一覧ページを表示するビュー。"""
    products = Product.objects.filter(is_active=True).order_by("-created_at")

    return render(request, "products/product_list.html", {"products": products})


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """商品詳細ページを表示するビュー。

    - URL の pk から対象の商品を取得する
    - 関連商品として、対象以外の最新4件の商品を取得する
    - 在庫数に応じて数量選択肢（quantity_range）を生成する
    - 上記をテンプレートに渡し、商品詳細ページを描画する
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # 自分自身（pk）が含まれないように除外し、新しい順に4件取得
    related_products = (
        Product.objects.filter(is_active=True)
        .exclude(pk=pk)
        .order_by("-created_at")[:4]
    )

    # 在庫数に基づいて選択可能な数量リストを生成
    quantity_range = get_quantity_range(product)

    context = {
        "product": product,
        "related_products": related_products,
        "quantity_range": quantity_range,
    }

    return render(request, "products/product_detail.html", context)


@auth
def manage_product_list(request: HttpRequest) -> HttpResponse:
    """
    商品管理画面（一覧）を表示するビュー。

    - Product を新しい順に全部取得する
    - manage_product_list.html に渡してテーブルで一覧表示する
    """
    products = Product.objects.all().order_by("-created_at")
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
    """
    商品管理画面：商品を削除するビュー。

    - GET: 対象商品の情報を表示し、「本当に削除してよいか」確認画面を出す
    - POST: 実際に Product を削除して一覧へリダイレクト
    """
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        return redirect("products:manage_product_list")

    # 初回アクセス時（GET）は確認画面用テンプレートを表示
    context = {
        "product": product,
    }
    return render(request, "products/manage_product_delete.html", context)


def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    カートの中身を表示するビュー。
    """
    if request.session.session_key is None:
        items = []
        cart_total = 0
        total_quantity = 0
        item_quantity_ranges = {}
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()
        if cart is None:
            items = []
            cart_total = 0
            total_quantity = 0
            item_quantity_ranges = {}
        else:
            items = CartItem.objects.select_related("product").filter(cart=cart)

            cart_total = sum(item.product.price * item.quantity for item in items)
            total_quantity = sum(item.quantity for item in items)

            # 各商品の在庫数に基づいた数量選択肢を生成
            item_quantity_ranges = {}
            for item in items:
                quantity_range = get_quantity_range(item.product)
                item_quantity_ranges[item.product.id] = quantity_range

    context = {
        "items": items,
        "cart_total": cart_total,
        "total_quantity": total_quantity,
        "item_quantity_ranges": item_quantity_ranges,
    }
    return render(request, "products/cart_detail.html", context)


@require_POST
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    カートに商品を追加するビュー。

    - 一覧画面からの追加: 数量は常に 1
    - 詳細画面からの追加: フォームから送られてきた quantity を使う
    """
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, pk=product_id)

    # 詳細画面から quantity が送られてくる想定。
    # 一覧画面からの追加は常に 1
    raw_quantity = request.POST.get("quantity", "1")
    try:
        quantity = int(raw_quantity)
    except ValueError:
        quantity = 1

    if quantity <= 0:
        quantity = 1

    # すでに同じ商品がカートに入っていたら数量だけ増やす
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )

    if not created:
        item.quantity += quantity
        item.save()

    return redirect("products:cart_detail")


@require_POST
def cart_item_update(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    カート内商品の数量を更新するビュー。
    """
    session_key = request.session.session_key
    if session_key is None:
        return JsonResponse({"ok": False}, status=400)

    cart = get_object_or_404(Cart, session_key=session_key)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    raw_quantity = request.POST.get("quantity", "")
    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        return JsonResponse({"ok": False}, status=400)

    # 0以下は無効なのでそのまま戻す
    if quantity <= 0:
        return JsonResponse({"ok": False}, status=400)

    # 在庫数を上限としてクリップ
    max_quantity = item.product.stock if item.product.stock > 0 else 1
    if quantity > max_quantity:
        quantity = max_quantity

    item.quantity = quantity
    item.save()

    items = CartItem.objects.select_related("product").filter(cart=cart)
    cart_total = sum(ci.product.price * ci.quantity for ci in items)
    total_quantity = sum(ci.quantity for ci in items)

    item_quantity_ranges = {
        ci.product.id: range(1, (ci.product.stock if ci.product.stock > 0 else 1) + 1)
        for ci in items
    }

    html = render_to_string(
        "products/_cart_summary.html",
        {
            "items": items,
            "cart_total": cart_total,
            "total_quantity": total_quantity,
            "item_quantity_ranges": item_quantity_ranges,
        },
        request=request,
    )

    return JsonResponse(
        {"ok": True, "html": html, "item_id": item_id, "quantity": quantity}
    )


@require_POST
def cart_item_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    # セッションキーから Cart を特定
    session_key = request.session.session_key
    if session_key is None:
        return redirect("products:cart_detail")

    cart = get_object_or_404(Cart, session_key=session_key)

    # 自分の Cart にぶら下がっている CartItem だけを削除対象にする
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    return redirect("products:cart_detail")
