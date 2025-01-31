from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth import login, authenticate
from .forms import RootSignUpForm, EmployeeAccountForm
from .models import User, Department
from sales.models import Product

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            if (user.department and user.department.name == '製品管理部') or user.account_type == 'root':
                context['total_products'] = Product.objects.count()
                
        return context

class RootSignupView(CreateView):
    form_class = RootSignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        account_id = form.instance.account_id
        password = form.cleaned_data.get("password1")
        user = authenticate(account_id=account_id, password=password)
        login(self.request, user)
        return response

class EmployeeAccountCreateView(UserPassesTestMixin, CreateView):
    form_class = EmployeeAccountForm
    template_name = "accounts/create_employee.html"
    success_url = reverse_lazy("accounts:employee_list")

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            (user.department and user.department.name == '人事部') or 
            user.account_type == 'root'
        )

class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'accounts/employee_list.html'
    context_object_name = 'employees'

    def test_func(self):
        user = self.request.user
        return (user.department and user.department.name == '人事部') or user.account_type == 'root'

    def get_queryset(self):
        return User.objects.filter(account_type='employee')

class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = EmployeeAccountForm
    template_name = 'accounts/edit_employee.html'
    success_url = reverse_lazy('accounts:employee_list')

    def test_func(self):
        user = self.request.user
        return (user.department and user.department.name == '人事部') or user.account_type == 'root'

class DepartmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Department
    template_name = 'accounts/department_list.html'
    context_object_name = 'departments'

    def test_func(self):
        user = self.request.user
        return (user.department and user.department.name == '人事部') or user.account_type == 'root'

class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Department
    template_name = 'accounts/department_form.html'
    fields = ['code', 'name']
    success_url = reverse_lazy('accounts:department_list')

    def test_func(self):
        user = self.request.user
        return (user.department and user.department.name == '人事部') or user.account_type == 'root'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '登録'
        return context

class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Department
    template_name = 'accounts/department_form.html'
    fields = ['code', 'name']
    success_url = reverse_lazy('accounts:department_list')

    def test_func(self):
        user = self.request.user
        return (user.department and user.department.name == '人事部') or user.account_type == 'root'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = '編集'
        return context

class DepartmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Department
    template_name = 'accounts/department_confirm_delete.html'
    success_url = reverse_lazy('accounts:department_list')

    def test_func(self):
        user = self.request.user
        return (user.department and user.department.name == '人事部') or user.account_type == 'root'