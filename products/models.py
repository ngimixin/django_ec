from tabnanny import verbose
from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=100, verbose_name="品番", unique=True)
    name = models.CharField(max_length=255, verbose_name="商品名")
    description = models.TextField(null=True, blank=True, verbose_name="商品説明")
    price = models.PositiveIntegerField(verbose_name="価格")
    stock = models.PositiveIntegerField(default=0, verbose_name="在庫数")
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="画像"
    )
    is_active = models.BooleanField(default=True, verbose_name="公開状態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name


class Cart(models.Model):
    session_key = models.CharField(
        max_length=64, unique=True, verbose_name="セッションキー"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"Cart(session_key={self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="カート"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.PositiveIntegerField(default=1, verbose_name="数量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name="注文者名")

    # 電話番号は先頭0・+81・ハイフンなどがあり得るため、数値ではなく文字列で保持する
    # 後から追加したカラムのため、既存レコード対応として NULL/blank を許可
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="注文者電話番号",
        help_text="配送時にご連絡させていただく事があります",
    )

    email = models.EmailField(verbose_name="注文者メールアドレス")

    # 日本の郵便番号は先頭0があり得る＆ハイフン入力にも対応したいので CharField
    # 後から追加したカラムのため、既存レコード対応として NULL/blank を許可
    postal_code = models.CharField(
        max_length=8,  # "123-4567" まで想定して8
        verbose_name="配送先郵便番号",
        null=True,
        blank=True,
    )

    # 日本国内向けフォームに寄せるが、DBは1カラムで保持する方針
    address = models.TextField(verbose_name="注文者住所")

    total_amount = models.PositiveIntegerField(verbose_name="合計金額")

    # チェックアウト時のクレジットカード情報（学習用）
    # 後から追加したカラムのため、既存レコード対応として NULL/blank を許可
    # ※ 実サービスではDBに保存しない
    card_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="カード番号",
    )

    card_expire = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="有効期限（MM/YY）",
    )

    card_cvv = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name="セキュリティコード",
    )

    card_holder = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="カード名義人",
    )

    class Status(models.TextChoices):
        PENDING = "pending", "未払い"
        PAID = "paid", "支払い済み"
        SHIPPED = "shipped", "発送済み"
        DELIVERED = "delivered", "配達済み"
        CANCELLED = "cancelled", "キャンセル"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="ステータス",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"Order #{self.id} ({self.name})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="注文"
    )
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, verbose_name="商品")
    price = models.PositiveIntegerField(verbose_name="単価")
    quantity = models.PositiveIntegerField(verbose_name="数量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"OrderItem(order_id={self.order_id}, product={self.product})"
