from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Пытаемся найти пользователя по email вместо username
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Если по email не нашли, можно попробовать по username (опционально)
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None