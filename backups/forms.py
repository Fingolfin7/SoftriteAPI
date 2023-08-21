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


class UploadBackupForm(forms.Form):
    # allow .zip files only
    file = forms.FileField(required=True, widget=forms.FileInput(attrs={'id': 'backup_field', 'accept': '.zip'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 1, 'cols': 115, 'placeholder': 'Add a comment...'})
        }
        labels = {k: "" for k in fields}
