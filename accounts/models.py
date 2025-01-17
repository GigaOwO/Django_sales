from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils.translation import gettext_lazy as _

# Create your models here.
class UserManager(BaseUserManager):
    def _create_user(self, email, account_id, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, account_id=account_id, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        
        return user

    def create_user(self, email, account_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email=email,
            account_id=account_id,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email, account_id, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self._create_user(
            email=email,
            account_id=account_id,
            password=password,
            **extra_fields,
        )

class User(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPES = (
        ('root', 'Root'),
        ('employee', 'Employee'),
    )
    
    account_id = models.CharField(
        verbose_name=_("account_id"),
        unique=True,
        max_length=10
    )
    account_type = models.CharField(
        verbose_name=_("account_type"),
        max_length=10,
        choices=ACCOUNT_TYPES,
        default='employee'
    )
    email = models.EmailField(
        verbose_name=_("email"),
        unique=True
    )
    first_name = models.CharField(
        verbose_name=_("first_name"),
        max_length=150,
        null=True,
        blank=False
    )
    last_name = models.CharField(
        verbose_name=_("last_name"),
        max_length=150,
        null=True,
        blank=False
    )
    is_staff = models.BooleanField(
        verbose_name=_("staff status"),
        default=False
    )
    is_superuser = models.BooleanField(
        verbose_name=_("is_superuser"),
        default=False
    )
    department = models.ForeignKey(
        'Department',
        verbose_name=_("department"),
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name=_("created_at"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated_at"),
        auto_now=True
    )
    objects = UserManager()

    USERNAME_FIELD = 'account_id'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.account_id

class Department(models.Model):
    """部署モデル"""
    code = models.CharField(
        verbose_name=_("部署コード"),
        max_length=10,
        unique=True
    )
    name = models.CharField(
        verbose_name=_("部署名"),
        max_length=100
    )
    created_at = models.DateTimeField(
        verbose_name=_("作成日時"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("更新日時"),
        auto_now=True
    )

    class Meta:
        verbose_name = _("部署")
        verbose_name_plural = _("部署一覧")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code}: {self.name}"