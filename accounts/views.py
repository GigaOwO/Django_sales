from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .forms import RootSignUpForm, EmployeeAccountForm
from django.contrib.auth import login, authenticate
from .models import User

class IndexView(TemplateView):
    template_name = "index.html"

class RootSignupView(CreateView):
    """ルートアカウント登録用ビュー"""
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
    """人事部用の社員アカウント発行ビュー"""
    form_class = EmployeeAccountForm
    template_name = "accounts/create_employee.html"
    success_url = reverse_lazy("accounts:employee_list")

    def test_func(self):
        # 人事部のアカウントのみアクセス可能
        return self.request.user.is_authenticated and \
               self.request.user.department == '人事部'

class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """社員一覧表示ビュー"""
    model = User
    template_name = 'accounts/employee_list.html'
    context_object_name = 'employees'

    def test_func(self):
        return self.request.user.department == '人事部'

    def get_queryset(self):
        return User.objects.filter(account_type='employee')

class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """社員情報編集ビュー"""
    model = User
    form_class = EmployeeAccountForm
    template_name = 'accounts/edit_employee.html'
    success_url = reverse_lazy('accounts:employee_list')

    def test_func(self):
        return self.request.user.department == '人事部'