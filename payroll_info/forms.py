from django import forms
from .models import *


class InterbankUSDRateForm(forms.ModelForm):
    class Meta:
        model = InterbankUSDRate
        fields = ['rate', 'date']
        widgets = {
            'rate': forms.NumberInput(attrs={'type': 'number', 'placeholder': 'Rate', 'class': 'width-90'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'width-90'})
        }
        labels = {k: "" for k in fields}


class NecForm(forms.ModelForm):
    class Meta:
        model = NEC
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'class': 'width-90'})
        }
        labels = {k: "" for k in fields}


class NecRatesForm(forms.ModelForm):
    class Meta:
        model = Rates
        fields = ['rate', 'date']
        widgets = {
            'rate': forms.NumberInput(attrs={'type': 'number', 'placeholder': 'Rate', 'required': True,
                                             'class': 'width-90'}),
            'date': forms.DateInput(attrs={'type': 'date', 'required': True, 'class': 'width-90'})}
        labels = {k: "" for k in fields}


class NECGradesForm(forms.ModelForm):
    class Meta:
        model = Grades
        fields = ['grade', 'usd_minimum']
        widgets = {
            'grade': forms.TextInput(attrs={'placeholder': 'Grade', 'required': False, 'class': 'width-90'}),
            'usd_minimum': forms.NumberInput(attrs={'placeholder': 'US Dollar Minimum', 'required': False,
                                                    'class': 'width-90'})
        }
        labels = {k: "" for k in fields}


class InterbankSearchForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date',
                                                                               'class': 'width-100',
                                                                               'required': False}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date',
                                                                             'class': 'width-100',
                                                                             'required': False}))
