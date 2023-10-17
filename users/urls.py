from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .forms import UserLoginForm



urlpatterns = [
    path('', views.profile, name='profile'),
    path('get-auth-token/', obtain_auth_token, name='get-auth-token'),
    path('check-auth-token/<token>', views.check_auth_token, name='check-auth-token'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html',
                                                authentication_form=UserLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html',
                                                                 html_email_template_name='users/Email Password Reset Template.html',
                                                                 subject_template_name='users/password_reset_subject.txt',
         success_url=reverse_lazy('password_reset_done')),
         name='password_reset'),
    # ref: https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.PasswordResetView

    path('password-reset/done/ ',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('register/', views.register, name='register'),
    path('create_new_users/', views.create_new_users, name='create_new_users'),
    path('delete_user/<int:pk>/', views.delete_user.as_view(), name='delete_user'),
    path('create_company/', views.CompanyCreateView.as_view(), name='create_company'),
    path('update_company/<int:pk>/', views.CompanyUpdateView.as_view(), name='update_company'),
    path('delete_company/<int:pk>/', views.CompanyDeleteView.as_view(), name='delete_company'),
    path('manage_companies/', views.CompanyListView.as_view(), name='manage_companies'),
    path('manage_company_users/<int:pk>', views.CompanyUserListView.as_view(), name='manage_company_users'),
]
