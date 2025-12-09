"""
カスタムデコレータ
"""

import base64
from functools import wraps
from django.http import HttpRequest, HttpResponse


def basic_auth_required(view_func):
    """
    Basic認証を要求するデコレータ。

    管理者専用の管理ページにアクセスする前に、
    ユーザー名とパスワードを確認するために使用します。

    認証情報:
        - ユーザー名: admin
        - パスワード: pw

    Args:
        view_func: デコレート対象のビュー関数。

    Returns:
        認証成功時は元のビュー関数を実行した結果。
        認証失敗時は 401 Unauthorized を返す。
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
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
        if username == "admin" and password == "pw":
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
