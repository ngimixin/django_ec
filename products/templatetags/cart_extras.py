from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """dict から安全に動的キーで値を取得するテンプレートフィルタ。"""
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except AttributeError:
        return None
