from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerUser, CartItem
from sales.models import Customer

class CustomerUserCreationForm(UserCreationForm):
    """顧客ユーザー登録フォーム"""
    customer_name = forms.CharField(max_length=100, label='会社名')
    phone_number = forms.CharField(max_length=15, label='電話番号')
    postal_code = forms.CharField(max_length=8, label='郵便番号')
    address = forms.CharField(max_length=200, label='住所')

    class Meta:
        model = CustomerUser
        fields = ('email', 'customer_name', 'phone_number', 'postal_code', 'address')

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # 得意先情報を作成
        customer = Customer.objects.create(
            customer_code=f"C{Customer.objects.count() + 1:05d}",  # 自動採番
            customer_name=self.cleaned_data['customer_name'],
            phone_number=self.cleaned_data['phone_number'],
            postal_code=self.cleaned_data['postal_code'],
            address=self.cleaned_data['address'],
            email=self.cleaned_data['email']
        )
        
        user.customer = customer
        if commit:
            user.save()
        return user

class CartItemForm(forms.ModelForm):
    """カート内商品フォーム"""
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'})
        }

class OrderConfirmationForm(forms.Form):
    """注文確認フォーム"""
    confirm = forms.BooleanField(
        required=True,
        label='注文内容を確認しました',
        help_text='上記の内容で注文を確定します。'
    )