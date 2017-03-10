__author__ = 'nibesh'

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser
from .utils import phone_regex
from django.utils.translation import ugettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    UserCreationForm.error_messages.update({
        'duplicate_username': "A user with that username already exists.",
        'duplicate_email': 'The email is already registered.'
    })

    class Meta:
        model = CustomUser
        exclude = []
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'], code='duplicate_username')

    def clean_email(self):
        email = self.cleaned_data['email']
        if email in (None,''):
            return None
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'], code='duplicate_email')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['password'].help_text = "Raw passwords are not stored, so there is no way to see " \
                                            "this user's password"
        # del self.fields['password']
        self.fields.keyOrder = ['mobile', 'email', 'username', 'full_name']

    class Meta:
        model = CustomUser
        exclude = ('groups', 'user_permissions', 'is_staff', 'is_active', 'date_joined', 'last_login', 'is_superuser',)


class ProfileImageForm(forms.Form):
    """
    Form to handle the profile image uploads
    """
    file = forms.FileField()


class MobileForm(forms.Form):
    """

    """
    error_messages = {
        'duplicate_mobile': 'The Mobile is already used by other user.'
    }
    mobile = forms.CharField(max_length=15, validators=[phone_regex])

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        try:
            c = CustomUser.objects.get(mobile=mobile)
            if c.mobile == mobile:
                return mobile
        except CustomUser.DoesNotExist:
            return mobile
        raise forms.ValidationError(self.error_messages['duplicate_mobile'], code='duplicate_mobile')


class NewUserSignUpForm(forms.Form):
    error_messages = {
        'duplicate_username': "A user with that username already exists.",
        'duplicate_email': 'The email is already registered.'
    }
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password",
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation",
                                widget=forms.PasswordInput,
                                help_text="Enter the same password as above, for verification.")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'], code='duplicate_username')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'], code='duplicate_email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    error_messages = {
            'invalid_login': _('The username credential is unknown.'),
            'invalid_pass': _('Invalid password or PIN'),
            'inactive': _('This account is inactive'),
        }    

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control' 
        self.fields['password'].widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data['username']
        if '@' in username:
            count = CustomUser.objects.filter(email=username).count()
            if count == 0:
                self._errors['username'] = self.error_class([_("Invalid Mail-ID")])
        else:
            count = CustomUser.objects.filter(username=username).count()
            if count == 0:
                self._errors['username'] = self.error_class([_("Invalid Username")])
        return username