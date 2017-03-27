from payment.models import BankAccount

__author__ = 'nibesh'

from django import forms
from .models import Trigger, Grid

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

class AddTriggerForm(forms.ModelForm):
    class Meta:
        model = Trigger
        fields = ('trigger_name',)


class GridForm(forms.ModelForm):

    # def __init__(self,user=None, *args, **kwargs):
    #     super(GridForm, self).__init__(*args, **kwargs)
    #     obj = Grid.objects.filter(dealer__id=user).first()
    #     print obj

        # self.fields['grid_row'].initial = object
        # self.fields['grid_column'].initial = object.grid_column

    class Meta:
        model = Grid
        fields = ('__all__')



class BankAccountEditForm(forms.ModelForm):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    account_holder_type = forms.ChoiceField(choices=[('individual', 'Individual'), ('company', 'Company')])
    class Meta:
        model = BankAccount
        fields = ('country','currency','routing_number','account_number','name','account_holder_type')
