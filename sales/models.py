from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncYear
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

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

    def get_current_stock(self):
        """現在の在庫数を取得"""
        try:
            return self.inventory.quantity
        except Inventory.DoesNotExist:
            return 0

    def is_low_stock(self):
        """在庫が安全在庫数を下回っているかチェック"""
        try:
            return self.inventory.quantity < self.inventory.safety_stock
        except Inventory.DoesNotExist:
            return True

    def create_inventory(self, initial_quantity=0, safety_stock=100):
        """在庫情報を新規作成"""
        if not hasattr(self, 'inventory'):
            Inventory.objects.create(
                product=self,
                quantity=initial_quantity,
                safety_stock=safety_stock
            )

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

    @classmethod
    def get_monthly_customer_summary(cls, year, month):
        """指定年月の得意先別受注集計を取得"""
        target_date = date(year, month, 1)
        next_month = target_date + relativedelta(months=1)
        
        amount_expression = ExpressionWrapper(
            F('quantity') * F('product__unit_price'),
            output_field=DecimalField()
        )
        
        return cls.objects.filter(
            order_date__gte=target_date,
            order_date__lt=next_month
        ).values(
            'customer__customer_code',
            'customer__customer_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum(amount_expression),
            order_count=Count('id')
        ).order_by('-total_amount')

    @classmethod
    def get_yearly_customer_summary(cls, year):
        """指定年の得意先別受注集計を取得"""
        target_date = date(year, 1, 1)
        next_year = date(year + 1, 1, 1)
        
        amount_expression = ExpressionWrapper(
            F('quantity') * F('product__unit_price'),
            output_field=DecimalField()
        )
        
        return cls.objects.filter(
            order_date__gte=target_date,
            order_date__lt=next_year
        ).values(
            'customer__customer_code',
            'customer__customer_name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum(amount_expression),
            order_count=Count('id')
        ).order_by('-total_amount')

    @classmethod
    def get_monthly_product_summary(cls, year, month):
        """指定年月の製品別受注集計を取得"""
        target_date = date(year, month, 1)
        next_month = target_date + relativedelta(months=1)
        
        amount_expression = ExpressionWrapper(
            F('quantity') * F('product__unit_price'),
            output_field=DecimalField()
        )
        
        return cls.objects.filter(
            order_date__gte=target_date,
            order_date__lt=next_month
        ).values(
            'product__product_code',
            'product__product_name',
            'product__unit_price'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum(amount_expression),
            order_count=Count('id')
        ).order_by('-total_amount')

    @classmethod
    def get_yearly_product_summary(cls, year):
        """指定年の製品別受注集計を取得"""
        target_date = date(year, 1, 1)
        next_year = date(year + 1, 1, 1)
        
        amount_expression = ExpressionWrapper(
            F('quantity') * F('product__unit_price'),
            output_field=DecimalField()
        )
        
        return cls.objects.filter(
            order_date__gte=target_date,
            order_date__lt=next_year
        ).values(
            'product__product_code',
            'product__product_name',
            'product__unit_price'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum(amount_expression),
            order_count=Count('id')
        ).order_by('-total_amount')

    @classmethod
    def get_monthly_trend(cls, year):
        """指定年の月別集計トレンドを取得"""
        target_date = date(year, 1, 1)
        next_year = date(year + 1, 1, 1)
        
        amount_expression = ExpressionWrapper(
            F('quantity') * F('product__unit_price'),
            output_field=DecimalField()
        )
        
        return cls.objects.filter(
            order_date__gte=target_date,
            order_date__lt=next_year
        ).annotate(
            month=TruncMonth('order_date')
        ).values('month').annotate(
            total_quantity=Sum('quantity'),
            total_amount=Sum(amount_expression),
            order_count=Count('id')
        ).order_by('month')

class Inventory(models.Model):
    """在庫モデル"""
    product = models.OneToOneField(
        Product, 
        on_delete=models.PROTECT,
        verbose_name="製品",
        related_name="inventory"
    )
    quantity = models.IntegerField("在庫数", default=0)
    safety_stock = models.IntegerField("安全在庫数", default=100)
    last_updated = models.DateTimeField("最終更新日", auto_now=True)

    class Meta:
        verbose_name = "在庫"
        verbose_name_plural = "在庫一覧"

    def __str__(self):
        return f"{self.product.product_name}の在庫"


class InventoryTransaction(models.Model):
    """在庫取引履歴モデル"""
    TRANSACTION_TYPES = [
        ('in', '入庫'),
        ('out', '出庫'),
        ('adjust', '在庫調整'),
    ]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.PROTECT,
        verbose_name="在庫",
        related_name="transactions"
    )
    transaction_type = models.CharField(
        "取引種類",
        max_length=10,
        choices=TRANSACTION_TYPES
    )
    quantity = models.IntegerField("数量")
    date = models.DateTimeField("取引日時", auto_now_add=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        verbose_name="関連受注",
        null=True,
        blank=True
    )
    note = models.CharField("備考", max_length=200, blank=True)

    class Meta:
        verbose_name = "在庫取引"
        verbose_name_plural = "在庫取引履歴"

    def clean(self):
        # 出庫時の在庫チェック
        if self.transaction_type == 'out':
            current_stock = self.inventory.quantity
            if current_stock < self.quantity:
                raise ValidationError(f'在庫不足です。現在の在庫数: {current_stock}')

    def save(self, *args, **kwargs):
        # 在庫数の更新
        if self.transaction_type == 'in':
            self.inventory.quantity += self.quantity
        elif self.transaction_type == 'out':
            self.inventory.quantity -= self.quantity
        elif self.transaction_type == 'adjust':
            self.inventory.quantity += self.quantity  # 調整値（正負両方あり得る）

        self.inventory.save()
        super().save(*args, **kwargs)