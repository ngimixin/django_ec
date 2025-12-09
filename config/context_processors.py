from django.conf import settings
from django.db.models import Sum
from django.http import HttpRequest

from products.models import Cart


def site_constants(request: HttpRequest) -> dict[str, str | int]:
    """SITE_TITLE などサイト共通の定数をテンプレートへ提供する。"""
    return {
        "SITE_TITLE": settings.SITE_TITLE,
        "COPYRIGHT_YEAR": settings.COPYRIGHT_YEAR,
    }


def cart_badge(request: HttpRequest) -> dict[str, int]:
    """
    ナビゲーションのカートバッジ用に、現在のカート内総数量を返す。

    - セッションが未作成、または Cart が存在しない場合は 0
    - CartItem の quantity 合計を集計して返す
    """
    session_key = request.session.session_key
    if session_key is None:
        return {"cart_total_quantity": 0}

    cart = Cart.objects.filter(session_key=session_key).first()
    if cart is None:
        return {"cart_total_quantity": 0}

    total_quantity = cart.items.aggregate(total=Sum("quantity")).get("total") or 0
    return {"cart_total_quantity": total_quantity}
