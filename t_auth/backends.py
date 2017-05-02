
from django import forms
from django.core.validators import validate_email
from django.contrib.auth.backends import ModelBackend

from .models import CustomUser


class EmailAuthBackend(ModelBackend):
    @staticmethod
    def _lookup_user(email_username):
        try:
            return CustomUser.objects.get(username=email_username)
        except CustomUser.DoesNotExist:
            try:
                validate_email(email_username)
                return CustomUser.objects.get(email=email_username.lower())
            except forms.ValidationError:
                return None
            except CustomUser.DoesNotExist:
                return None

    def authenticate(self, username=None, password=None, **kwargs):
        """

        :param username:
        :param password:
        :param kwargs:
        :return:
        """
        if username is None:
            username = kwargs.get('username')
        user = self._lookup_user(username)
        if user:
            if user.check_password(password):
                user.backend = "%s.%s" % (self.__module__, self.__class__.__name__)
                return user
        return None

    def get_user(self, user_id):
        """

        :param user_id:
        :return:
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
