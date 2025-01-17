from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'email', 'first_name', 'last_name', 'department', 'account_type')
    list_filter = ('account_type', 'department', 'is_staff')
    search_fields = ('account_id', 'email', 'first_name', 'last_name')
    ordering = ('account_id',)

admin.site.unregister(Group)