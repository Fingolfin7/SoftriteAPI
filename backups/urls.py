from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload, name='upload'),
    path('delete/<int:pk>', views.BackupDeleteView.as_view(), name='delete'),
    path('list', views.BackupListView.as_view(), name='list'),
]
