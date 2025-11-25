from django.http import HttpRequest
from django.conf import settings


def site_constants(request: HttpRequest) -> dict[str, str | int]:
    """SITE_TITLE などサイト共通の定数をテンプレートへ提供する。"""
    return {
        "SITE_TITLE": settings.SITE_TITLE,
        "COPYRIGHT_YEAR": settings.COPYRIGHT_YEAR,
    }
