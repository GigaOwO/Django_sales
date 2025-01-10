from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Customer, Product, Order

class CustomerListView(LoginRequiredMixin, ListView):
    """得意先一覧"""
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'

    def get_queryset(self):
        """営業部のみ全データ表示、他部署は参照のみ"""
        queryset = super().get_queryset()
        if self.request.user.department != '営業部':
            queryset = queryset.none()
        return queryset

class CustomerCreateView(LoginRequiredMixin, CreateView):
    """得意先登録"""
    model = Customer
    template_name = 'sales/customer_form.html'
    fields = ['customer_code', 'customer_name', 'phone_number', 
              'postal_code', 'address', 'email']
    success_url = reverse_lazy('sales:customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '登録'
        return context

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    """得意先編集"""
    model = Customer
    template_name = 'sales/customer_form.html'
    fields = ['customer_code', 'customer_name', 'phone_number', 
              'postal_code', 'address', 'email']
    success_url = reverse_lazy('sales:customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '編集'
        return context

    def test_func(self):
        return self.request.user.department == '営業部'

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    """得意先削除"""
    model = Customer
    template_name = 'sales/customer_confirm_delete.html'
    success_url = reverse_lazy('sales:customer_list')

    def test_func(self):
        return self.request.user.department == '営業部'


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