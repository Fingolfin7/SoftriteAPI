"""SoftriteAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users import views as user_views
from users.forms import UserLoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payroll_info/', include("payroll_info.urls")),
    path('backups/', include(("backups.urls", "backups"), namespace='backups')),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html',
                                                authentication_form=UserLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', user_views.register, name='register'),
    path('', user_views.profile, name='profile'),
    path('create_new_users/', user_views.create_new_users, name='create_new_users'),
    path('create_company/', user_views.CompanyCreateView.as_view(), name='create_company'),
    path('update_company/<int:pk>/', user_views.CompanyUpdateView.as_view(), name='update_company'),
    path('delete_company/<int:pk>/', user_views.CompanyDeleteView.as_view(), name='delete_company'),
    path('manage_companies/', user_views.CompanyListView.as_view(), name='manage_companies'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)