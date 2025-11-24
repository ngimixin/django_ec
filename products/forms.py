from django import forms
from .models import Product


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
