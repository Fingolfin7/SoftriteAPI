from django import forms
from .models import Profile, Company
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'width-100'}),
                               label="")

    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'width-100'}),
                             label="")

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password',
                                          'autocomplete': 'on', 'class': 'width-100'}),
        label=""
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                          'autocomplete': 'on', 'class': 'width-100'}),
        label=""
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        # help_texts = {k: "" for k in fields}
        # labels = {k: "" for k in fields}


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'width-100'}),
                             label="")
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter Password', 'autocomplete': 'on', 'class': 'width-100'}),
        label="")


class CompanyCreateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Name'}),
                           label="")
    code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Code'}),
                           label="")
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Address'}),
                              label="")
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Phone'}),
                            label="")
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Company Email'}),
                             label="")
    website = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'Company Website'}),
                             label="")
    logo = forms.ImageField(widget=forms.FileInput(), label="")

    class Meta:
        model = Company
        fields = ['name', 'code', 'address', 'phone', 'email', 'website', 'logo']
        help_texts = {k: "" for k in fields}
        labels = {k: "" for k in fields}


class UpdateProfileForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput())
    firstname = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
                                label="")
    lastname = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
                               label="")
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}),
                            label="")

    class Meta:
        model = Profile
        fields = ['image', 'firstname', 'lastname', 'phone']
        help_texts = {k: "" for k in fields}
        labels = {k: "" for k in fields}
