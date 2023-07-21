from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from backups.models import Backup
from django.contrib import messages


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


def login(request):
    if request == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            print('here')
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
        profile_form = UpdateProfileForm(request.POST, request.FILES,
                                         instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UpdateProfileForm(instance=request.user.profile)

    backups = Backup.objects.filter(user=request.user).order_by('-date_uploaded')[0:5]  # get the 5 most recent backups
    return render(request, 'users/profile.html', {'profile_form': profile_form,
                                                  'title': 'Profile',
                                                  'backups': backups})


@login_required
def create_new_users(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        profile_form = UpdateProfileForm(request.POST)

        if user_form.is_valid():
            created_user = user_form.save()
            profile_form.instance = created_user.profile

            if profile_form.is_valid():
                # check if company field is set/exists, if not set the company to the company of the requesting user
                if not profile_form.cleaned_data['company'] and request.user.profile.company:
                    created_user.instance.company = request.user.profile.company

                profile_form.save()
                messages.success(request, f'User {created_user.username} created successfully.')
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


class CompanyListView(ListView):
    model = Company
    template_name = 'users/company_list.html'
    context_object_name = 'companies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = CompanySearchForm(
            initial={
                'name': self.request.GET.get('name', ''),
                'code': self.request.GET.get('code', ''),
            }

        )
        context['title'] = 'Manage Companies'
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        code = self.request.GET.get('code')

        if name:
            queryset = queryset.filter(name__icontains=name)
        if code:
            queryset = queryset.filter(code__icontains=code)

        return queryset


class CompanyCreateView(CreateView):
    model = Company
    fields = ['name', 'code', 'address', 'phone', 'email', 'website', 'logo']
    template_name = 'users/company_form.html'
    success_url = 'create_company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Company'
        return context

    def form_valid(self, form):  # add success message
        messages.success(self.request, 'Company created successfully.')
        return super().form_valid(form)


class CompanyUpdateView(UpdateView):
    model = Company
    fields = ['name', 'code', 'address', 'phone', 'email', 'website', 'logo']
    template_name = 'users/company_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Company Information'
        return context

    def form_valid(self, form):  # add success message
        messages.success(self.request, 'Company Information Updated.')
        return super().form_valid(form)


class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'users/company_confirm_delete.html'
    success_url = 'create_company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Company'
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Company deleted successfully.')
        return super().delete(request, *args, **kwargs)

