from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from django.views.generic import ListView
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
