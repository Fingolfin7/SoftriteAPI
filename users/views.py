import logging
from .forms import *
from SoftriteAPI.settings import EMAIL_HOST_USER
from backups.models import Backup
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

logger = logging.getLogger(__name__)


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Error creating account. Please try again.')

    else:
        form = UserRegisterForm()
    return render(request, 'users/signup.html', {'form': form, 'title': 'Register'})


class delete_user(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete User'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)


def login(request):
    if request == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Login successful.')
            return redirect('profile')
        else:
            messages.error(request, 'Error logging in. Please try again.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form, 'title': 'Login'})


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        profile_form.fields['is_company_admin'].disabled = True

        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating profile. Please try again.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    backups = Backup.objects.filter(user=request.user).order_by('-date_uploaded')[0:5]  # get the 5 most recent backups
    return render(request, 'users/profile.html',
                  {
                      'user_form': user_form,
                      'profile_form': profile_form,
                      'title': 'Profile',
                      'backups': backups
                  })


def send_new_user_credentials(user, password: str):
    html_body = render_to_string('users/Email Account Credentials Template.html', {'user': user, 'password': password})
    plain_text_body = strip_tags(html_body)


    send_mail(
        subject='Adaski Account Credentials',
        message=plain_text_body,
        html_message=html_body,
        from_email=EMAIL_HOST_USER,
        recipient_list=[user.email],
    )
    logger.info(f"New user credentials sent to {user.username}({user.email}) from {user.profile.company.name}")


@login_required
def create_new_users(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = UpdateProfileForm(request.POST)

        if user_form.is_valid():
            # get the email and username from the form
            password = user_form.cleaned_data['password1']
            created_user = user_form.save()
            profile_form.instance = created_user.profile

            if profile_form.is_valid():
                # check if company field is set/exists, if not set the company to the company of the requesting user
                if not profile_form.cleaned_data['company'] and request.user.profile.company:
                    company = request.user.profile.company
                else:
                    company = profile_form.cleaned_data['company']

                profile_form.save()

                # save the company selected in the profile form to the user's profile separately
                created_user.profile.company = company
                created_user.profile.save()

                # send the new user an email with their credentials
                send_new_user_credentials(created_user, password)

                messages.success(request, f'{created_user.username} created successfully.')
                return redirect('create_new_users')
            else:
                messages.error(request, 'Error adding user. Please try again.')

        else:
            messages.error(request, 'Error adding user. Please try again.')
    else:
        user_form = UserRegisterForm()
        profile_form = UpdateProfileForm()
    return render(request, 'users/create_users.html', {'user_form': user_form,
                                                       'profile_form': profile_form, 'title': 'Add User'})


class CompanyUserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(pk=self.kwargs['pk'])
        context['search_form'] = UserSearchForm(
            initial={
                'username': self.request.GET.get('username', ''),
                'email': self.request.GET.get('email', ''),
            }
        )
        context['title'] = 'Manage Users'
        return context

    def get_queryset(self):
        queryset = super().get_queryset().filter(profile__company=self.kwargs['pk'])  # only get users from the company
        queryset = queryset.exclude(pk=self.request.user.pk)  # exclude the requesting user from the list
        username = self.request.GET.get('username')
        email = self.request.GET.get('email')

        if username:
            queryset = queryset.filter(username__icontains=username)
        if email:
            queryset = queryset.filter(email__icontains=email)

        return queryset


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'users/company_list.html'
    context_object_name = 'companies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CompanySearchForm(
            initial={
                'name': self.request.GET.get('name', ''),
            }

        )
        context['title'] = 'Manage Companies'
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    fields = ['name', 'address', 'phone', 'email', 'website', 'logo']
    template_name = 'users/company_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Company'
        return context

    def get_success_url(self):
        return reverse('update_company', kwargs={'pk': self.object.pk})

    def form_valid(self, form):  # add success message
        messages.success(self.request, 'Company created successfully.')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'address', 'phone', 'email', 'website', 'logo']
    template_name = 'users/company_form.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Company Information'
        context['form'] = CompanyForm(instance=self.get_object())
        context['company_accounts'] = Profile.objects.filter(company=self.get_object()).exclude(user=self.request.user)[
                                      0:5]
        return context

    def get_object(self, queryset=None):
        return Company.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('update_company', kwargs={'pk': self.object.pk})

    def form_valid(self, form):  # add success message
        messages.success(self.request, 'Company Information Updated.')
        return super().form_valid(form)


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'users/company_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Company'
        return context

    def get_success_url(self):
        return reverse('manage_companies')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Company deleted successfully.')
        return super().delete(request, *args, **kwargs)

