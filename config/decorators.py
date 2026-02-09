"""
カスタムデコレータ
"""

import base64
import os
from functools import wraps
from django.http import HttpRequest, HttpResponse


def basic_auth_required(view_func):
    """
    Basic認証を要求するデコレータ。

    認証情報は環境変数から取得する。
    - BASIC_AUTH_USER
    - BASIC_AUTH_PASSWORD
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        basic_user = os.getenv("BASIC_AUTH_USER")
        basic_password = os.getenv("BASIC_AUTH_PASSWORD")

        if not basic_user or not basic_password:
            return HttpResponse(
                "Basic認証が未設定です",
                status=500,
                content_type="text/plain; charset=utf-8",
            )

        # Authorizationヘッダーを取得
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Basic "):
            # Basic認証が提供されていない場合、401を返す
            response = HttpResponse(
                "認証が必要です", status=401, content_type="text/plain; charset=utf-8"
            )
            response["WWW-Authenticate"] = 'Basic realm="ProductManagement"'
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

        # Basic認証の認証情報をデコード
        try:
            auth_decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = auth_decoded.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            response = HttpResponse(
                "認証情報が無効です",
                status=401,
                content_type="text/plain; charset=utf-8",
            )
            response["WWW-Authenticate"] = 'Basic realm="ProductManagement"'
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

        # 認証情報を検証
        if username == basic_user and password == basic_password:
            return view_func(request, *args, **kwargs)

        response = HttpResponse(
            "認証に失敗しました", status=401, content_type="text/plain; charset=utf-8"
        )
        response["WWW-Authenticate"] = 'Basic realm="ProductManagement"'
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    return _wrapped_view
