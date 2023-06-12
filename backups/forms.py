from django import forms
from .models import *


class BackupSearch(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date',
                                                                               'class': 'width-100',
                                                                               'required': False}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date',
                                                                             'class': 'width-100',
                                                                             'required': False}))
    name = forms.CharField(required=False, widget=forms.DateInput(attrs={'class': 'width-100',
                                                                         'required': False}))
