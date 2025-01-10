from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import uuid

class RootSignUpForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        # ルートアカウントの設定
        user.account_type = 'root'
        user.is_staff = True
        user.is_superuser = True
        # アカウントIDの自動生成 (R + UUID末尾8文字)
        user.account_id = 'R' + str(uuid.uuid4())[-8:]
        
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )

class EmployeeAccountForm(UserCreationForm):
    DEPARTMENT_CHOICES = [
        ('営業部', '営業部'),
        ('製造部', '製造部'),
        ('製品管理部', '製品管理部'),
        ('経理部', '経理部'),
        ('人事部', '人事部'),
    ]

    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, label='Department')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_type = 'employee'
        user.account_id = 'E' + str(uuid.uuid4())[-8:]
        user.department = self.cleaned_data['department']
        
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "department",
        )