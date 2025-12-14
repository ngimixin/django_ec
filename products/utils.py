from .models import Product


def get_quantity_range(product: Product, max_per_order: int | None = None) -> list[int]:
    """
    在庫数に基づいて選択可能な数量リストを返す。

    Args:
        product: 対象の商品インスタンス
        max_per_order: 1回の注文で選択可能な最大数量（オプション）

    Returns:
        1から在庫数（またはmax_per_order）までの整数リスト
    """
    stock = product.stock if product.stock > 0 else 1
    if max_per_order is not None:
        stock = min(stock, max_per_order)
    return list(range(1, stock + 1))
