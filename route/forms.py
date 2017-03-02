__author__ = 'nibesh'

from django import forms


class OrderReadyForm(forms.Form):
    message = forms.CharField(max_length=160)

