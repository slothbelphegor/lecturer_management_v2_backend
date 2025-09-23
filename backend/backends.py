from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

User = get_user_model()

class EmailOrUsernameModelBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email_validator = EmailValidator()
        try:
            # Check if the username is a valid email
            is_email = True
            try:
                email_validator(username)
            except ValidationError:
                is_email = False

            # Query based on email or username
            if is_email:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)

            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None