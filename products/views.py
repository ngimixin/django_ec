import logging

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from products.services.cart import get_or_create_cart

from .models import Product, Cart, CartItem, Order, OrderItem
from config.decorators import basic_auth_required as auth
from .forms import ProductForm, OrderCreateForm
from .utils import get_quantity_range

logger = logging.getLogger(__name__)


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
    return render(request, "manage/products/product_list.html", context)


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
    return render(request, "manage/products/product_create.html", context)


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

    return render(request, "manage/products/product_edit.html", context)


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
    return render(request, "manage/products/product_delete.html", context)


@auth
def manage_order_list(request: HttpRequest) -> HttpResponse:
    """
    購入明細一覧を表示するビュー（管理者向け）。
    """
    orders = Order.objects.order_by("-created_at")
    context = {
        "orders": orders,
    }
    return render(request, "manage/orders/order_list.html", context)


@auth
def manage_order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    購入明細詳細を表示するビュー（管理者向け）。
    """
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=pk,
    )
    context = {
        "order": order,
        "items": order.items.order_by("created_at"),
    }
    return render(request, "manage/orders/order_detail.html", context)


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
            items = (
                CartItem.objects.select_related("product")
                .filter(cart=cart)
                .order_by("created_at")
            )

            available_items = [item for item in items if item.product.stock > 0]
            cart_total = sum(
                item.product.price * item.quantity for item in available_items
            )
            total_quantity = sum(item.quantity for item in available_items)

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
    return render(request, "cart/cart_detail.html", context)


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

    redirect_url = request.META.get("HTTP_REFERER")
    if product.stock <= 0:
        messages.error(
            request,
            f"在庫切れのためカートに追加できません。（{product.name}）",
        )
        if redirect_url:
            return redirect(redirect_url)
        return redirect("products:product_list")

    existing_item = CartItem.objects.filter(cart=cart, product=product).first()
    existing_quantity = existing_item.quantity if existing_item else 0
    if existing_quantity + quantity > product.stock:
        messages.error(
            request,
            f"在庫数を超えるためカートに追加できません。（{product.name}）",
        )
        if redirect_url:
            return redirect(redirect_url)
        return redirect("products:product_list")

    if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)

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

    # 在庫が0の場合は更新不可
    max_quantity = item.product.stock
    if max_quantity <= 0:
        return JsonResponse({"ok": False}, status=409)
    if quantity > max_quantity:
        quantity = max_quantity

    item.quantity = quantity
    item.save()

    items = (
        CartItem.objects.select_related("product")
        .filter(cart=cart)
        .order_by("created_at")
    )
    available_items = [ci for ci in items if ci.product.stock > 0]
    cart_total = sum(ci.product.price * ci.quantity for ci in available_items)
    total_quantity = sum(ci.quantity for ci in available_items)

    item_quantity_ranges = {
        ci.product.id: get_quantity_range(ci.product) for ci in items
    }

    html = render_to_string(
        "cart/_cart_summary.html",
        {
            "items": items,
            "cart_total": cart_total,
            "total_quantity": total_quantity,
            "item_quantity_ranges": item_quantity_ranges,
        },
        request=request,
    )

    return JsonResponse(
        {
            "ok": True,
            "html": html,
            "item_id": item_id,
            "quantity": quantity,
            "total_quantity": total_quantity,
        }
    )


@require_POST
def cart_item_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    session_key = request.session.session_key
    if session_key is None:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False}, status=400)
        return redirect("products:cart_detail")

    cart = get_object_or_404(Cart, session_key=session_key)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        items = (
            CartItem.objects.select_related("product")
            .filter(cart=cart)
            .order_by("created_at")
        )
        available_items = [ci for ci in items if ci.product.stock > 0]
        cart_total = sum(
            ci.product.price * ci.quantity for ci in available_items
        )
        total_quantity = sum(ci.quantity for ci in available_items)
        item_quantity_ranges = {
            ci.product.id: get_quantity_range(ci.product) for ci in items
        }

        html = render_to_string(
            "cart/_cart_summary.html",
            {
                "items": items,
                "cart_total": cart_total,
                "total_quantity": total_quantity,
                "item_quantity_ranges": item_quantity_ranges,
            },
            request=request,
        )
        return JsonResponse(
            {
                "ok": True,
                "html": html,
                "total_quantity": total_quantity,
            }
        )

    return redirect("products:cart_detail")


def _send_mail_after_commit(order_id: int) -> None:
    """注文確認メールを送信する。"""
    try:
        order = Order.objects.prefetch_related("items").get(pk=order_id)

        subject = f"【VELO STATION】ご購入明細（注文番号：{order.id}）"
        message = render_to_string(
            "orders/emails/order_confirmation.txt",
            {
                "order": order,
                "items": order.items.order_by("created_at"),
            },
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    except Exception:
        # 注文自体は確定済みなので、メール失敗で注文フローを壊さない（ログだけ残す）
        logger.exception(
            "Failed to send order confirmation email (order_id=%s)", order_id
        )


@require_POST
def order_create(request: HttpRequest) -> HttpResponse:
    """
    注文を作成するビュー。
    """
    form = OrderCreateForm(request.POST)

    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart = Cart.objects.filter(session_key=session_key).first()
    if not cart:
        messages.warning(request, "カートに商品がありません。")
        return redirect("products:product_list")

    cart_items = (
        CartItem.objects.select_related("product")
        .filter(cart=cart)
        .order_by("created_at")
    )
    if not cart_items.exists():
        messages.warning(request, "カートに商品がありません。")
        return redirect("products:product_list")

    if not form.is_valid():
        items = list(cart_items)
        product_ids = [item.product_id for item in items]
        current_products = Product.objects.in_bulk(product_ids)
        for item in items:
            current_product = current_products.get(item.product_id)
            if current_product:
                item.product = current_product
                if (
                    current_product.stock > 0
                    and item.quantity > current_product.stock
                ):
                    item.quantity = current_product.stock
                    item.save(update_fields=["quantity"])
                    messages.warning(
                        request,
                        f"在庫数に合わせて数量を変更しました。（{current_product.name}）",
                    )
        available_items = [item for item in items if item.product.stock > 0]
        cart_total = sum(
            item.product.price * item.quantity for item in available_items
        )
        total_quantity = sum(item.quantity for item in available_items)
        item_quantity_ranges = {}
        for item in items:
            quantity_range = get_quantity_range(item.product)
            item_quantity_ranges[item.product.id] = quantity_range

        context = {
            "items": items,
            "cart_total": cart_total,
            "total_quantity": total_quantity,
            "item_quantity_ranges": item_quantity_ranges,
            "form": form,
        }
        return render(request, "cart/cart_detail.html", context)

    order: Order | None = None

    with transaction.atomic():
        items = list(cart_items)
        product_ids = [item.product_id for item in items]
        locked_products = Product.objects.select_for_update().in_bulk(product_ids)

        has_errors = False
        has_adjustments = False
        for item in items:
            product = locked_products.get(item.product_id)
            if product is None:
                messages.error(
                    request,
                    f"商品が存在しないため購入できません。カートから削除してください。（{item.product.name}）",
                )
                has_errors = True
                continue

            item.product = product

            if product.stock <= 0:
                messages.error(
                    request,
                    f"在庫切れのためご注文を確定できません。カートから削除してください。（{product.name}）",
                )
                has_errors = True
                continue

            if product.stock < item.quantity:
                item.quantity = product.stock
                item.save(update_fields=["quantity"])
                messages.warning(
                    request,
                    f"在庫数に合わせて数量を変更しました。（{product.name}）",
                )
                has_adjustments = True

        if has_errors or has_adjustments:
            available_items = [ci for ci in items if ci.product.stock > 0]
            cart_total = sum(
                item.product.price * item.quantity for item in available_items
            )
            total_quantity = sum(item.quantity for item in available_items)
            item_quantity_ranges = {}
            for item in items:
                quantity_range = get_quantity_range(item.product)
                item_quantity_ranges[item.product.id] = quantity_range
            return render(
                request,
                "cart/cart_detail.html",
                {
                    "items": items,
                    "cart_total": cart_total,
                    "total_quantity": total_quantity,
                    "item_quantity_ranges": item_quantity_ranges,
                    "form": form,
                },
            )

        # 在庫を更新
        for item in items:
            product = locked_products[item.product_id]
            product.stock -= item.quantity
            product.save(update_fields=["stock"])

        # 注文を作成
        order = form.save(commit=False)

        total_amount = 0
        # OrderItemをまとめてINSERTしてDB往復回数を減らす
        order_items: list[OrderItem] = []

        for item in items:
            product = locked_products[item.product_id]
            total_amount += product.price * item.quantity
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,  # 注文時点の商品名
                    price=product.price,  # 注文時点の単価
                    quantity=item.quantity,
                )
            )

        order.total_amount = total_amount
        order.save()

        OrderItem.objects.bulk_create(order_items)
        cart.delete()

        order_id = order.id
        transaction.on_commit(lambda: _send_mail_after_commit(order_id))

    assert order is not None
    request.session["last_order_id"] = order.id
    messages.success(request, "注文完了メールを送信しました。")
    return redirect("products:order_complete")


def order_complete(request: HttpRequest) -> HttpResponse:
    """
    注文完了ページを表示するビュー。
    """
    order_id = request.session.get("last_order_id")
    if not order_id:
        return redirect("products:product_list")

    order = get_object_or_404(Order, id=order_id)
    request.session.pop("last_order_id", None)

    return render(
        request,
        "orders/order_complete.html",
        {
            "order": order,
            "items": order.items.order_by("created_at"),
        },
    )
