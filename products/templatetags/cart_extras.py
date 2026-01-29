import re
from typing import Any, Mapping

from django import template

register = template.Library()


@register.filter
def get_item(mapping: Mapping[Any, Any] | None, key: Any) -> Any | None:
    """dict から安全に動的キーで値を取得するテンプレートフィルタ。"""
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.filter
def format_phone(value: Any) -> str:
    """電話番号を見やすいハイフン付き形式に整形する。"""
    if value is None:
        return ""
    digits = re.sub(r"\D", "", str(value))
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    if len(digits) == 10:
        if digits.startswith(("03", "06")):
            return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return str(value)
