from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'customer'

urlpatterns = [
    # 認証関連
    path('register/', views.CustomerRegistrationView.as_view(), name='register'),
    path('login/', views.CustomerLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='customer:login'), name='logout'),
    
    # 製品カタログ
    path('catalog/', views.ProductCatalogView.as_view(), name='catalog'),
    
    # カート関連
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:pk>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:pk>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    # 注文関連
    path('order/confirm/', views.OrderConfirmationView.as_view(), name='order_confirm'),
    path('order/complete/', views.OrderCompletionView.as_view(), name='order_complete'),
    path('order/history/', views.OrderHistoryView.as_view(), name='order_history'),
]