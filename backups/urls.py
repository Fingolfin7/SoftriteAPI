from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload, name='upload'),
    path('manual_upload', views.manual_upload, name='manual_upload'),
    path('delete/<int:pk>', views.BackupDeleteView.as_view(), name='delete'),
    path('user_list', views.BackupListView.as_view(), name='user_list'),
    path('company_list/<int:company_id>', views.CompanyBackupListView.as_view(), name='company_list'),
]
