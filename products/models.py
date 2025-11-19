from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="商品名")
    description = models.TextField(blank=True, verbose_name="商品説明")
    price = models.PositiveIntegerField(verbose_name="価格")
    stock = models.PositiveIntegerField(default=0, verbose_name="在庫数")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="画像")
    