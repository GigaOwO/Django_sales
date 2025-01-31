from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from sales.models import Customer

class CustomerUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('メールアドレスは必須です')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomerUser(AbstractBaseUser, PermissionsMixin):
    """顧客ユーザーモデル"""
    email = models.EmailField(_('メールアドレス'), unique=True)
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_('得意先情報'),
        related_name='user_account'
    )
    is_active = models.BooleanField(_('有効'), default=True)
    is_staff = models.BooleanField(_('管理者'), default=False)
    date_joined = models.DateTimeField(_('登録日時'), auto_now_add=True)

    # 権限関連のフィールドにrelated_nameを追加
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='customer_user_set'  # この行を追加
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customer_user_set'  # この行を追加
    )

    objects = CustomerUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('顧客ユーザー')
        verbose_name_plural = _('顧客ユーザー一覧')

    def __str__(self):
        return f"{self.email} ({self.customer.customer_name})"

class Cart(models.Model):
    """ショッピングカートモデル"""
    user = models.OneToOneField(
        CustomerUser,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('カート')
        verbose_name_plural = _('カート一覧')

class CartItem(models.Model):
    """カート内商品モデル"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'sales.Product',
        on_delete=models.CASCADE,
        verbose_name=_('製品')
    )
    quantity = models.PositiveIntegerField(_('数量'), default=1)
    added_at = models.DateTimeField(_('追加日時'), auto_now_add=True)

    class Meta:
        verbose_name = _('カート内商品')
        verbose_name_plural = _('カート内商品一覧')
        unique_together = ['cart', 'product']  # 同じ製品は1つのみ（数量で管理）

    @property
    def subtotal(self):
        """小計を計算"""
        return self.quantity * self.product.unit_price