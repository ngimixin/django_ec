from django.db import transaction
from django.http import HttpRequest

from products.models import Cart


def get_or_create_cart(request: HttpRequest) -> Cart:
    """
    現在のセッションに紐づく Cart を取得 or 作成するヘルパー。

    - まだセッションIDがない場合は save() して session_key を発行させる
    - session_key を元に Cart を get_or_create する
    """
    if request.session.session_key is None:
        request.session.save()

    session_key = request.session.session_key

    with transaction.atomic():
        cart, _created = Cart.objects.get_or_create(session_key=session_key)

    return cart