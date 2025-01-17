from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Department
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
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label='Department',
        required=True
    )

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