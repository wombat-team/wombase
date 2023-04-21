from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmployeeBackend(ModelBackend):
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        user_model = get_user_model()

        if not phone_number:
            phone_number = kwargs.get('username')

        if not (user := user_model.objects.filter(phone_number=phone_number).first()):
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
