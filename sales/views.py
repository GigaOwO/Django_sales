from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Customer, Product, Order, Inventory, InventoryTransaction
from datetime import datetime, date

class CustomerListView(LoginRequiredMixin, ListView):
    """得意先一覧"""
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    ordering = ['customer_code']  # コード順にソート

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # ルートユーザーまたは営業部のユーザーは編集可能
        context['can_edit'] = user.account_type == 'root' or (
            user.department and user.department.name == '営業部'
        )
        return context

class CustomerCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """得意先登録"""
    model = Customer
    template_name = 'sales/customer_form.html'
    fields = ['customer_code', 'customer_name', 'phone_number', 
              'postal_code', 'address', 'email']
    success_url = reverse_lazy('sales:customer_list')

    def test_func(self):
        # ルートユーザーまたは営業部のユーザーのみ作成可能
        user = self.request.user
        return user.account_type == 'root' or (
            user.department and user.department.name == '営業部'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '登録'
        return context

    def form_valid(self, form):
        """フォームが有効な場合の処理"""
        response = super().form_valid(form)
        messages.success(self.request, f'得意先「{form.instance.customer_name}」を登録しました。')
        return response

class CustomerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """得意先編集"""
    model = Customer
    template_name = 'sales/customer_form.html'
    fields = ['customer_code', 'customer_name', 'phone_number', 
              'postal_code', 'address', 'email']
    success_url = reverse_lazy('sales:customer_list')

    def test_func(self):
        # ルートユーザーまたは営業部のユーザーのみ編集可能
        user = self.request.user
        return user.account_type == 'root' or (
            user.department and user.department.name == '営業部'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '編集'
        return context

class CustomerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """得意先削除"""
    model = Customer
    template_name = 'sales/customer_confirm_delete.html'
    success_url = reverse_lazy('sales:customer_list')

    def test_func(self):
        # ルートユーザーまたは営業部のユーザーのみ削除可能
        user = self.request.user
        return user.account_type == 'root' or (
            user.department and user.department.name == '営業部'
        )

    def delete(self, request, *args, **kwargs):
        """削除成功時にメッセージを表示"""
        result = super().delete(request, *args, **kwargs)
        messages.success(request, '得意先を削除しました。')
        return result

class ProductListView(LoginRequiredMixin, ListView):
    """製品一覧"""
    model = Product
    template_name = 'sales/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        """製品管理部のみ全データを編集可能、他部署は参照のみ"""
        queryset = super().get_queryset()
        return queryset

class ProductCreateView(LoginRequiredMixin, CreateView):
    """製品登録"""
    model = Product
    template_name = 'sales/product_form.html'
    fields = ['product_code', 'product_name', 'unit_price']
    success_url = reverse_lazy('sales:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '登録'
        return context

    def test_func(self):
        return self.request.user.department == '製品管理部'

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """製品編集"""
    model = Product
    template_name = 'sales/product_form.html'
    fields = ['product_code', 'product_name', 'unit_price']
    success_url = reverse_lazy('sales:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '編集'
        return context

    def test_func(self):
        return self.request.user.department == '製品管理部'

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """製品削除"""
    model = Product
    template_name = 'sales/product_confirm_delete.html'
    success_url = reverse_lazy('sales:product_list')

    def test_func(self):
        return self.request.user.department == '製品管理部'


class OrderAccessMixin(UserPassesTestMixin):
    """営業部のみ編集可能、他部署は参照のみ可能にするMixin"""
    def test_func(self):
        return self.request.user.department == '営業部'

    def handle_no_permission(self):
        return redirect('sales:order_list')

class OrderListView(LoginRequiredMixin, ListView):
    """受注一覧"""
    model = Order
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'
    ordering = ['-order_date']

class OrderDetailView(LoginRequiredMixin, DetailView):
    """受注詳細"""
    model = Order
    template_name = 'sales/order_detail.html'
    context_object_name = 'order'

class OrderCreateView(LoginRequiredMixin, OrderAccessMixin, CreateView):
    """受注登録"""
    model = Order
    template_name = 'sales/order_form.html'
    fields = ['order_code', 'customer', 'product', 'quantity', 'order_date', 'delivery_date']
    success_url = reverse_lazy('sales:order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '登録'
        return context

class OrderUpdateView(LoginRequiredMixin, OrderAccessMixin, UpdateView):
    """受注編集"""
    model = Order
    template_name = 'sales/order_form.html'
    fields = ['order_code', 'customer', 'product', 'quantity', 'order_date', 'delivery_date', 'delivered_date']
    success_url = reverse_lazy('sales:order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '編集'
        return context

class OrderDeleteView(LoginRequiredMixin, OrderAccessMixin, DeleteView):
    """受注削除"""
    model = Order
    template_name = 'sales/order_confirm_delete.html'
    success_url = reverse_lazy('sales:order_list')

    def delete(self, request, *args, **kwargs):
        """削除成功時にメッセージを表示"""
        result = super().delete(request, *args, **kwargs)
        from django.contrib import messages
        messages.success(request, '受注情報を削除しました。')
        return result


class InventoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """在庫数更新ビュー"""
    model = Inventory
    template_name = 'sales/inventory_form.html'
    fields = ['quantity', 'safety_stock']
    success_url = reverse_lazy('sales:product_list')

    def test_func(self):
        """製品管理部のみアクセス可能"""
        return self.request.user.department == '製品管理部'

    def form_valid(self, form):
        """在庫数更新時に取引履歴を記録"""
        old_quantity = self.get_object().quantity
        new_quantity = form.cleaned_data['quantity']
        adjustment = new_quantity - old_quantity

        response = super().form_valid(form)

        if adjustment != 0:
            InventoryTransaction.objects.create(
                inventory=self.object,
                transaction_type='adjust',
                quantity=adjustment,
                note='手動在庫調整'
            )
            messages.success(self.request, f'在庫数を{new_quantity}に更新しました。')

        return response

class InventoryTransactionListView(LoginRequiredMixin, ListView):
    """在庫取引履歴一覧"""
    model = InventoryTransaction
    template_name = 'sales/inventory_transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date']

    def get_queryset(self):
        queryset = super().get_queryset()
        inventory_id = self.kwargs.get('inventory_id')
        if inventory_id:
            queryset = queryset.filter(inventory_id=inventory_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_id = self.kwargs.get('inventory_id')
        if inventory_id:
            context['inventory'] = get_object_or_404(Inventory, id=inventory_id)
        return context

class InventoryTransactionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """在庫取引登録ビュー"""
    model = InventoryTransaction
    template_name = 'sales/inventory_transaction_form.html'
    fields = ['transaction_type', 'quantity', 'note']
    
    def test_func(self):
        return self.request.user.department == '製品管理部'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_id = self.kwargs.get('inventory_id')
        context['inventory'] = get_object_or_404(Inventory, id=inventory_id)
        return context

    def form_valid(self, form):
        inventory_id = self.kwargs.get('inventory_id')
        form.instance.inventory = get_object_or_404(Inventory, id=inventory_id)
        
        try:
            response = super().form_valid(form)
            messages.success(self.request, '在庫取引を登録しました。')
            return response
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('sales:inventory_transaction_list', kwargs={'inventory_id': self.object.inventory.id})



class OrderSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'sales/order_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 年月の取得（デフォルトは現在の年月）
        year = int(self.request.GET.get('year', datetime.now().year))
        month = int(self.request.GET.get('month', datetime.now().month))
        
        # 利用可能な年のリストを生成（例：過去3年分）
        current_year = datetime.now().year
        context['available_years'] = list(range(current_year - 2, current_year + 1))
        
        # 月のリストを生成
        context['months'] = [(i, f"{i}月") for i in range(1, 13)]
        
        # 各種集計データの取得
        context.update({
            'selected_year': year,
            'selected_month': month,
            'monthly_customer_summary': Order.get_monthly_customer_summary(year, month),
            'yearly_customer_summary': Order.get_yearly_customer_summary(year),
            'monthly_product_summary': Order.get_monthly_product_summary(year, month),
            'yearly_product_summary': Order.get_yearly_product_summary(year),
            'monthly_trend': Order.get_monthly_trend(year),
        })
        
        return context