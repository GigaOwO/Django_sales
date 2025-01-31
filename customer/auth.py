from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import CustomerUser

class CustomerAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')

        if username is None or password is None:
            return None

        try:
            user = CustomerUser.objects.get(email=username)
        except CustomerUser.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomerUser.objects.get(pk=user_id)
        except CustomerUser.DoesNotExist:
            return None