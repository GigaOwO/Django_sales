from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('signup/', views.RootSignupView.as_view(), name="signup"),  # SignupView から RootSignupView に変更
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='accounts:index'), name='logout'),
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeAccountCreateView.as_view(), name='create_employee'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='edit_employee'),
]