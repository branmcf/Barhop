__author__ = 'nibesh'

from django import forms

#
# class PaymentForm(forms.Form):
#     stripeToken = forms.CharField()
#     stripeTokenType = forms.CharField()
#     stripeEmail = forms.EmailInput()


class PriceSubmissionForm(forms.Form):
    amount = forms.IntegerField(help_text='Amount in Cents Eg: 2000 for $20.00')
    detail = forms.CharField(widget=forms.Textarea())
