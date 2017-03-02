__author__ = 'nibesh'

from django import forms

COUNTRY_CHOICES = [('AU', 'Australia'), ('CA', 'Canada'), ('DK', 'Denmark'), ('FI', 'Finland'), ('IE', 'Ireland'),
                   ('NO', 'Norway'), ('SE', 'SWEDEN'), ('GB', 'United Kingdom'), ('US', 'United States')]

CURRENCY_CHOICES = [('AUD', 'Australian Dollar'), ('CAD', 'Canadian Dollar'), ('USD', 'United States Dollar'),
                    ('DKK', 'Danish Krane'), ('NOK', 'Norwegian Krone'), ('SEK', 'Swedish Krona'), ('EUR', 'Euro'),
                    ('GBP', 'British Pound')]


class BankAccountCreationForm(forms.Form):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    routing_number = forms.CharField()
    account_number = forms.CharField()
    name = forms.CharField()
    account_holder_type = forms.ChoiceField(choices=[('individual', 'Individual'), ('company', 'Company')])


class ManagedAccountCreationForm(forms.Form):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, label='Country of Operation')
