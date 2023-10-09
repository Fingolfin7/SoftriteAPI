from django import forms
from .models import Profile, Company
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}),
                               label="")

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


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'required': False}),
                                 label="", required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'required': False}),
                                label="", required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
                             label="")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        help_texts = {k: "" for k in fields}
        labels = {k: "" for k in fields}


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'width-100'}),
                             label="")
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Enter Password', 'autocomplete': 'on', 'class': 'width-100'}),
        label="")


class CompanyForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Name', 'required': False}),
                           label="")
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Address', 'required': False}),
                              required=False, label="")
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Phone', 'required': False}),
                            required=False, label="")
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Company Email', 'required': False}),
                             required=False, label="")
    website = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'Company Website', 'required': False}),
                             required=False, label="")
    logo = forms.ImageField(widget=forms.FileInput(), required=False,
                            label="")

    class Meta:
        model = Company
        fields = ['name', 'address', 'phone', 'email', 'website', 'logo']
        help_texts = {k: "" for k in fields}
        labels = {k: "" for k in fields}


class UpdateProfileForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(), required=False)
    is_company_admin = forms.BooleanField(required=False, label="")
    get_backup_emails = forms.BooleanField(required=False, label="")
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=False, label="")  # select a company
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}), required=False,
                            label="")

    class Meta:
        model = Profile
        fields = ['image', 'phone', 'is_company_admin', 'get_backup_emails']
        help_texts = {k: "" for k in fields}
        labels = {k: "" for k in fields}


class CompanySearchForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Company Name'}),
                           label="")


class UserSearchForm(forms.Form):
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Username'}),
                               label="")
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                            label="")
