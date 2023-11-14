from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('get_backups_list/', views.get_backups_list, name='get_backups_list'),
    path('get_backups_list/<str:company_code>/', views.get_backups_list, name='get_backups_list'),
    path('get_directories/', views.get_directories, name='get_directories_list'),
    path('download_backup/<int:backup_id>/', views.download_backup, name='download_backup'),
    path('manual_upload/', views.manual_upload, name='manual_upload'),
    path('delete/<int:pk>/', views.BackupDeleteView.as_view(), name='delete'),
    path('user_list/', views.BackupListView.as_view(), name='user_list'),
    path('company_list/<int:company_id>/', views.CompanyBackupListView.as_view(), name='company_list'),
    path('backup_detail/<int:pk>/', views.BackupDetailView.as_view(), name='backup_details'),
    path('file_browser/', views.file_browser_view, name='file_browser'),
]
