from django import forms
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), label="")

    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
                             label="")

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password',
                                          'autocomplete': 'on'}),
        label=""
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                          'autocomplete': 'on'}),
        label=""
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        # help_texts = {k: "" for k in fields}
        # labels = {k: "" for k in fields}


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'placeholder': 'Username'}),
                             label="")
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter Password', 'autocomplete': 'on'}),
        label="")


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image']
        widgets = {
            'image': forms.FileInput(),
        }
        help_texts = {k: "" for k in fields}
        labels = {k: "" for k in fields}


