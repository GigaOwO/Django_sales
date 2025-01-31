from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, 
    DetailView, TemplateView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.transaction import atomic
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .models import CustomerUser, Cart, CartItem
from .forms import CustomerUserCreationForm, CartItemForm, OrderConfirmationForm
from sales.models import Product, Order
from datetime import date, timedelta

class CustomerLoginView(LoginView):
    template_name = 'customer/login.html'
    
    def get_success_url(self):
        return reverse_lazy('customer:catalog')
    
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = form.get_user()
        if hasattr(user, 'customer'):
            login(self.request, user)
            return super().form_valid(form)
        form.add_error(None, 'メールアドレスまたはパスワードが正しくありません。')
        return self.form_invalid(form)

class CustomerRegistrationView(CreateView):
    """顧客ユーザー登録ビュー"""
    template_name = 'customer/register.html'
    form_class = CustomerUserCreationForm
    success_url = reverse_lazy('customer:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '登録が完了しました。ログインしてください。')
        return response

class ProductCatalogView(ListView):
    """製品カタログ一覧ビュー"""
    model = Product
    template_name = 'customer/product_catalog.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(inventory__quantity__gt=0)  # 在庫がある商品のみ表示

class CartView(LoginRequiredMixin, ListView):
    """カート内容表示ビュー"""
    template_name = 'customer/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.user.cart
        context['total'] = sum(item.subtotal for item in cart.items.all())
        return context

class AddToCartView(LoginRequiredMixin, FormView):
    """カートに商品を追加するビュー"""
    form_class = CartItemForm
    template_name = 'customer/add_to_cart.html'

    def get_success_url(self):
        return reverse_lazy('customer:cart')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = get_object_or_404(Product, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        
        # 在庫チェック
        if product.inventory.quantity < form.cleaned_data['quantity']:
            messages.error(self.request, '在庫が不足しています。')
            return self.form_invalid(form)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': form.cleaned_data['quantity']}
        )

        if not created:
            cart_item.quantity += form.cleaned_data['quantity']
            cart_item.save()

        messages.success(self.request, 'カートに追加しました。')
        return super().form_valid(form)

class UpdateCartItemView(LoginRequiredMixin, UpdateView):
    """カート内商品の数量更新ビュー"""
    model = CartItem
    form_class = CartItemForm
    template_name = 'customer/update_cart_item.html'
    success_url = reverse_lazy('customer:cart')

    def form_valid(self, form):
        if form.instance.product.inventory.quantity < form.cleaned_data['quantity']:
            messages.error(self.request, '在庫が不足しています。')
            return self.form_invalid(form)
        return super().form_valid(form)

class RemoveFromCartView(LoginRequiredMixin, DeleteView):
    """カートから商品を削除するビュー"""
    model = CartItem
    success_url = reverse_lazy('customer:cart')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'カートから商品を削除しました。')
        return super().delete(request, *args, **kwargs)

class OrderConfirmationView(LoginRequiredMixin, FormView):
    """注文確認ビュー"""
    template_name = 'customer/order_confirm.html'
    form_class = OrderConfirmationForm
    success_url = reverse_lazy('customer:order_complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.user.cart
        context['cart_items'] = cart.items.all()
        context['total'] = sum(item.subtotal for item in cart.items.all())
        context['delivery_date'] = date.today() + timedelta(days=30)  # 30日後を納期とする
        return context

    @atomic
    def form_valid(self, form):
        user = self.request.user
        cart = user.cart
        
        # 在庫の最終チェック
        for item in cart.items.all():
            if item.product.inventory.quantity < item.quantity:
                messages.error(self.request, f'{item.product.product_name}の在庫が不足しています。')
                return self.form_invalid(form)

        # 受注データの作成
        for item in cart.items.all():
            order = Order.objects.create(
                order_code=f"WEB{Order.objects.count() + 1:06d}",
                customer=user.customer,
                product=item.product,
                quantity=item.quantity,
                order_date=date.today(),
                delivery_date=date.today() + timedelta(days=30)
            )

        # カートを空にする
        cart.items.all().delete()
        
        messages.success(self.request, '注文が完了しました。')
        return super().form_valid(form)

class OrderCompletionView(LoginRequiredMixin, TemplateView):
    """注文完了ビュー"""
    template_name = 'customer/order_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_date'] = date.today() + timedelta(days=30)
        return context

class OrderHistoryView(LoginRequiredMixin, ListView):
    """注文履歴一覧ビュー"""
    template_name = 'customer/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(
            customer=self.request.user.customer
        ).order_by('-order_date')