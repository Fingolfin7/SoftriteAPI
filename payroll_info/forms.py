from django import forms
from .models import *


class InterbankUSDRateForm(forms.ModelForm):
    class Meta:
        model = InterbankUSDRate
        fields = ['rate', 'date']
        widgets = {
            'rate': forms.NumberInput(attrs={'placeholder': 'Rate'}),
            'date': forms.DateInput(attrs={'type': 'date'})
        }
        labels = {k: "" for k in fields}


class NecForm(forms.ModelForm):
    class Meta:
        model = NEC
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'required': 'True'})
        }
        labels = {k: "" for k in fields}


class NecRatesForm(forms.ModelForm):
    class Meta:
        model = Rates
        fields = ['rate', 'date']
        widgets = {
            'rate': forms.NumberInput(attrs={'placeholder': 'Rate', 'required': 'True'}),
            'date': forms.DateInput(attrs={'type': 'date', 'required': 'True'})}
        labels = {k: "" for k in fields}


class NECGradesForm(forms.ModelForm):
    class Meta:
        model = Grades
        fields = ['grade', 'usd_minimum']
        widgets = {
            'grade': forms.TextInput(attrs={'placeholder': 'Grade', 'required': 'False'}),
            'usd_minimum': forms.NumberInput(attrs={'placeholder': 'US Dollar Minimum', 'required': 'False'})
        }
        labels = {k: "" for k in fields}
