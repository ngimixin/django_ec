import unicodedata

from django import forms
from django.utils import timezone

from .models import Product, Order, PromotionCode


class ProductForm(forms.ModelForm):
    """Productモデル用の入力フォーム"""

    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "is_active",
        ]
        widgets = {
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class OrderCreateForm(forms.ModelForm):
    """
    チェックアウト用の注文フォーム。

    - Checkout画面で入力させる「注文者情報」と「支払い情報（学習用）」をまとめる
    - total_amount はカート合計からサーバ側で計算して Order に入れるので、フォームでは扱わない
    """

    # Orderモデルに無い項目は「フォームの追加フィールド」としてここで定義する
    prefecture = forms.CharField()
    city = forms.CharField()
    street = forms.CharField()
    building = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = [
            # --- 注文者情報 ---
            "name",
            "phone",
            "email",
            "postal_code",
            # address はDBに保存する最終結果。ユーザー入力は prefecture/city/street から作る
            "address",
            # --- クレジットカード情報（学習用） ---
            "card_number",
            "card_expire",
            "card_cvv",
            "card_holder",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 受け取るデータとしての必須項目
        required_fields = [
            "name",
            "phone",
            "email",
            "postal_code",
            "prefecture",
            "city",
            "street",
            "card_number",
            "card_expire",
            "card_cvv",
            "card_holder",
        ]

        required_messages = {
            "name": "氏名は必須です。",
            "phone": "電話番号は必須です。",
            "email": "メールアドレスは必須です。",
            "postal_code": "郵便番号は必須です。",
            "prefecture": "都道府県は必須です。",
            "city": "市区町村は必須です。",
            "street": "丁目・番地・号は必須です。",
            "card_number": "カード番号は必須です。",
            "card_expire": "有効期限は必須です。",
            "card_cvv": "セキュリティコードは必須です。",
            "card_holder": "カード名義人は必須です。",
        }

        # 必須項目のエラーメッセージの設定
        for field_name in required_fields:
            self.fields[field_name].required = True
            self.fields[field_name].error_messages["required"] = required_messages[
                field_name
            ]

        # address はフォーム入力から組み立てるため、直接入力は不要
        self.fields["address"].required = False

        # メールアドレスのエラーメッセージの設定
        self.fields["email"].error_messages[
            "invalid"
        ] = "メールアドレスは半角で入力してください（例：example@example.com）。"

    def _extract_digits(self, value: str) -> str:
        """
        文字列から数字のみを抽出し、半角数字に正規化する。

        - 全角数字は半角数字に変換される
        - ハイフンやスペースなどの記号は除去される

        Args:
            value: 抽出元の文字列

        Returns:
            半角数字のみを含む文字列
        """
        return unicodedata.normalize(
            "NFKC", "".join(ch for ch in value if ch.isdigit())
        )

    def clean_phone(self) -> str:
        """
        電話番号の簡易チェック（数字だけに整形）。

        - 入力に「-」やスペースが混ざっても除去し、半角数字に変換する
        - 桁数はざっくり 10〜11 桁を想定（日本の携帯/固定の一般的な範囲）
        """
        phone = (self.cleaned_data.get("phone") or "").strip()
        digits_only = self._extract_digits(phone)

        if not (10 <= len(digits_only) <= 11):
            raise forms.ValidationError("電話番号は10〜11桁の数字で入力してください。")

        return digits_only

    def clean_card_number(self) -> str:
        """
        カード番号の簡易チェック（学習用）。

        - 入力に「-」やスペースが混ざっても除去し、半角数字に変換する
        - 13〜19桁（カード番号の一般的な範囲）でチェック
        """
        value = (self.cleaned_data.get("card_number") or "").strip()
        digits_only = self._extract_digits(value)

        if not (13 <= len(digits_only) <= 19):
            raise forms.ValidationError(
                "カード番号は13〜19桁の数字で入力してください。"
            )

        return digits_only

    def clean_postal_code(self) -> str:
        """
        郵便番号の簡易チェック。

        - 入力に「-」やスペースが混ざっても除去し、半角数字に変換する
        - ７桁の数字に整形する
        """
        value = (self.cleaned_data.get("postal_code") or "").strip()
        digits_only = self._extract_digits(value)

        # 日本の郵便番号は7桁固定
        if len(digits_only) != 7:
            raise forms.ValidationError("郵便番号は7桁の数字で入力してください。")

        return digits_only

    def clean_card_expire(self) -> str:
        """
        有効期限（MM/YY）の簡易チェック（学習用）。

        - 「MM/YY」形式のみ許容
        - 全角英数字は半角英数字に変換する
        - 月は 01〜12 の範囲でチェック
        - 期限切れ（今月より前）を弾く
        """
        value = (self.cleaned_data.get("card_expire") or "").strip()
        normalized_value = unicodedata.normalize("NFKC", value)

        # MM/YY 形式チェック
        if "/" not in normalized_value:
            raise forms.ValidationError("有効期限は MM/YY 形式で入力してください。")

        try:
            month_str, year_str = normalized_value.split("/")
            month_str = month_str.strip()
            year_str = year_str.strip()
        except ValueError:
            raise forms.ValidationError("有効期限は MM/YY 形式で入力してください。")

        # 数字チェック
        if not (month_str.isdigit() and year_str.isdigit()):
            raise forms.ValidationError("有効期限は MM/YY 形式で入力してください。")

        # 年は2桁固定（MM/YY の YY）
        if len(year_str) != 2:
            raise forms.ValidationError("有効期限は MM/YY 形式で入力してください。")

        month = int(month_str)
        # 月は 1〜12 の範囲のみ許可
        if not (1 <= month <= 12):
            raise forms.ValidationError(
                "有効期限の月は 01〜12 の範囲で入力してください。"
            )

        # 期限切れを弾く
        today = timezone.localdate()
        current_yy = today.year % 100
        current_mm = today.month

        input_yy = int(year_str)
        input_mm = month

        if (input_yy, input_mm) < (current_yy, current_mm):
            raise forms.ValidationError("有効期限が過去になっています。")

        # 表示揺れを防ぐため MM/YY に正規化
        return f"{input_mm:02d}/{year_str}"

    def clean_card_cvv(self) -> str:
        """
        セキュリティコード（CVV）の簡易チェック（学習用）。

        - 全角数字は半角数字に変換する
        - 3〜4桁の数字のみ許容
        """
        value = (self.cleaned_data.get("card_cvv") or "").strip()
        normalized_value = unicodedata.normalize("NFKC", value)

        if not normalized_value.isdigit():
            raise forms.ValidationError("セキュリティコードは数字で入力してください。")

        if not (3 <= len(normalized_value) <= 4):
            raise forms.ValidationError(
                "セキュリティコードは3〜4桁で入力してください。"
            )

        return normalized_value

    def clean_card_holder(self) -> str:
        """
        カード名義人の簡易正規化（学習用）。

        - 前後の空白を削除
        - 連続する空白を1個にまとめる
        - 大文字に正規化する
        """
        value = (self.cleaned_data.get("card_holder") or "").strip()

        # 連続スペースを1個に正規化（"TARO   TANAKA" → "TARO TANAKA"）
        normalized = " ".join(value.split())

        # 学習用のため大文字化（実務ではDBに保存しない）
        return normalized.upper()

    def clean(self):
        """
        住所関連フィールドを結合し、address に格納する。

        - prefecture/city/street が揃っている場合に住所を組み立てる。
        - building は任意（存在する場合のみ追加）
        """
        cleaned_data = super().clean()

        prefecture = (cleaned_data.get("prefecture") or "").strip()
        city = (cleaned_data.get("city") or "").strip()
        street = (cleaned_data.get("street") or "").strip()
        building = (cleaned_data.get("building") or "").strip()

        if prefecture and city and street:
            address = f"{prefecture}{city}{street}"
            if building:
                address = f"{address} {building}"
            cleaned_data["address"] = address

        return cleaned_data


class PromotionCodeApplyForm(forms.Form):
    """プロモーションコードの適用フォーム。"""

    promotion_code = forms.CharField(max_length=7)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.promotion: PromotionCode | None = None

        self.fields["promotion_code"].error_messages[
            "required"
        ] = "プロモーションコードを入力してください。"

    def clean_promotion_code(self) -> str:
        raw_value = (self.cleaned_data.get("promotion_code") or "").strip()
        normalized = unicodedata.normalize("NFKC", raw_value).upper()

        if len(normalized) != 7 or not normalized.isalnum():
            raise forms.ValidationError(
                "プロモーションコードは7桁の英数字で入力してください。"
            )

        promotion = PromotionCode.objects.filter(
            code__iexact=normalized, is_used=False
        ).first()
        if not promotion:
            raise forms.ValidationError("プロモーションコードが無効です。")

        self.promotion = promotion
        return normalized
