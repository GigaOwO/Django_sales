from django.db import models
from django.utils import timezone

class Customer(models.Model):
    """得意先モデル"""
    customer_code = models.CharField("得意先コード", max_length=10, unique=True)
    customer_name = models.CharField("得意先名", max_length=100)
    phone_number = models.CharField("電話番号", max_length=15)
    postal_code = models.CharField("郵便番号", max_length=8)
    address = models.CharField("住所", max_length=200)
    email = models.EmailField("メールアドレス")
    
    class Meta:
        verbose_name = "得意先"
        verbose_name_plural = "得意先一覧"

    def __str__(self):
        return f"{self.customer_code}: {self.customer_name}"

class Product(models.Model):
    """製品モデル"""
    product_code = models.CharField("製品コード", max_length=10, unique=True)
    product_name = models.CharField("製品名", max_length=100)
    unit_price = models.DecimalField("単価", max_digits=10, decimal_places=0)
    
    class Meta:
        verbose_name = "製品"
        verbose_name_plural = "製品一覧"

    def __str__(self):
        return f"{self.product_code}: {self.product_name}"

class Order(models.Model):
    """受注モデル"""
    order_code = models.CharField("受注コード", max_length=10, unique=True)
    customer = models.ForeignKey(Customer, verbose_name="得意先", on_delete=models.PROTECT)
    product = models.ForeignKey(Product, verbose_name="製品", on_delete=models.PROTECT)
    quantity = models.IntegerField("数量")
    order_date = models.DateField("受注日", default=timezone.now)
    delivery_date = models.DateField("納品予定日")
    delivered_date = models.DateField("納品日", null=True, blank=True)
    
    class Meta:
        verbose_name = "受注"
        verbose_name_plural = "受注一覧"

    def __str__(self):
        return f"{self.order_code}: {self.customer.customer_name} - {self.product.product_name}"

    @property
    def total_amount(self):
        """合計金額を計算"""
        return self.quantity * self.product.unit_price