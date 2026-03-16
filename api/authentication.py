# authentication.py
from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class NumeroAuthBackend(ModelBackend):
    def authenticate(self, request, numero=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(numero=numero)
            if user.check_password(password):
                return user
        except Usuario.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None