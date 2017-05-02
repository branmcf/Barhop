
from django import forms

from trophy.models import TrophyModel


class TrophyForm(forms.ModelForm):
    class Meta:
        model = TrophyModel
        fields = ['trophy', 'message', 'default_order_response']

    def clean_trophy(self):
        trophy = self.cleaned_data['trophy']
        if not trophy:
            raise forms.ValidationError('This Field is required.')
        return trophy

    def clean_message(self):
        message = self.cleaned_data['message']
        if not message:
            raise forms.ValidationError('This field is required.')
        return message
