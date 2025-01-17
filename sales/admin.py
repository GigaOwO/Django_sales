from django.contrib import admin
from .models import Customer, Product, Order, Inventory, InventoryTransaction

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_code', 'customer_name', 'phone_number', 'postal_code', 'address')
    search_fields = ('customer_code', 'customer_name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'unit_price')
    search_fields = ('product_code', 'product_name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'customer', 'product', 'quantity', 'order_date', 'delivery_date', 'delivered_date')
    list_filter = ('order_date', 'delivery_date', 'delivered_date')
    search_fields = ('order_code', 'customer__customer_name', 'product__product_name')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'safety_stock', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('product__product_name', 'product__product_code')

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('inventory', 'transaction_type', 'quantity', 'date', 'note')
    list_filter = ('transaction_type', 'date')
    search_fields = ('inventory__product__product_name', 'note')