from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm
from django.contrib.auth import login, authenticate


# Create your views here.
class IndexView(TemplateView):
    """ ホームビュー """
    template_name = "index.html"

class SignupView(CreateView):
    """ ユーザー登録用ビュー """
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        account_id = form.cleaned_data.get("account_id")
        password = form.cleaned_data.get("password1")
        user = authenticate(account_id=account_id, password=password)
        login(self.request, user)
        return response