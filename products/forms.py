from django.utils import timezone
from django import forms
from .models import Product, Order


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

    class Meta:
        model = Order
        fields = [
            # --- 注文者情報 ---
            "name",
            "phone",
            "email",
            "postal_code",
            "address",
            # --- クレジットカード情報（学習用） ---
            "card_number",
            "card_expire",
            "card_cvv",
            "card_holder",
        ]
        widgets = {
            # --- 注文者情報 ---
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "山田 太郎"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "000-0000-0000"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "you@example.com"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "000-0000"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "住所"}
            ),
            # --- クレジットカード情報（学習用） ---
            "card_number": forms.TextInput(
                # NOTE: ハイフンは入力されがちなので、バリデーション側で無視する
                attrs={"class": "form-control", "placeholder": "0000 0000 0000 0000"}
            ),
            "card_expire": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "MM/YY"}
            ),
            "card_cvv": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "000"}
            ),
            "card_holder": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "TARO TANAKA"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 画面表示上は必須にする項目
        required_fields = [
            "name",
            "phone",
            "email",
            "postal_code",
            "address",
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
            "address": "住所は必須です。",
            "card_number": "カード番号は必須です。",
            "card_expire": "有効期限は必須です。",
            "card_cvv": "セキュリティコードは必須です。",
            "card_holder": "カード名義人は必須です。",
        }

        for field_name in required_fields:
            self.fields[field_name].required = True

            # Django のデフォルト「このフィールドは必須です。」を、狙った文言に置き換える
            self.fields[field_name].error_messages["required"] = required_messages[
                field_name
            ]

    def clean_phone(self) -> str:
        """
        電話番号の簡易チェック（数字だけに整形）。

        - 入力に「-」やスペースが混ざってもOKにする
        - 桁数はざっくり 10〜11 桁を想定（日本の携帯/固定の一般的な範囲）
        """
        phone = (self.cleaned_data.get("phone") or "").strip()
        digits_only = "".join(ch for ch in phone if ch.isdigit())

        if not (10 <= len(digits_only) <= 11):
            raise forms.ValidationError("電話番号は10〜11桁の数字で入力してください。")

        return digits_only

    def clean_card_number(self) -> str:
        """
        カード番号の簡易チェック（学習用）。

        - 入力にスペースやハイフンが混ざってもOKにする
        - 13〜19桁（カード番号の一般的な範囲）でチェック
        """
        value = (self.cleaned_data.get("card_number") or "").strip()
        digits_only = "".join(ch for ch in value if ch.isdigit())

        if not (13 <= len(digits_only) <= 19):
            raise forms.ValidationError(
                "カード番号は13〜19桁の数字で入力してください。"
            )

        return digits_only

    def clean_postal_code(self) -> str:
        """
        郵便番号の簡易チェック。

        - 「123-4567」「1234567」どちらも許容
        - 数字だけに整形して保存する
        """
        value = (self.cleaned_data.get("postal_code") or "").strip()
        digits_only = "".join(ch for ch in value if ch.isdigit())

        # 日本の郵便番号は7桁固定
        if len(digits_only) != 7:
            raise forms.ValidationError("郵便番号は7桁の数字で入力してください。")

        return digits_only

    def clean_card_expire(self) -> str:
        """
        有効期限（MM/YY）の簡易チェック（学習用）。

        - 「MM/YY」形式のみ許容
        - 月は 01〜12 の範囲でチェック
        - 期限切れ（今月より前）を弾く
        """
        value = (self.cleaned_data.get("card_expire") or "").strip()

        # MM/YY 形式チェック
        if "/" not in value:
            raise forms.ValidationError("有効期限は MM/YY 形式で入力してください。")

        try:
            month_str, year_str = value.split("/")
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
        return f"{month_str.zfill(2)}/{year_str}"

    def clean_card_cvv(self) -> str:
        """
        セキュリティコード（CVV）の簡易チェック（学習用）。

        - 3〜4桁の数字のみ許容
        """
        value = (self.cleaned_data.get("card_cvv") or "").strip()

        if not value.isdigit():
            raise forms.ValidationError("セキュリティコードは数字で入力してください。")

        if not (3 <= len(value) <= 4):
            raise forms.ValidationError(
                "セキュリティコードは3〜4桁で入力してください。"
            )

        return value

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
