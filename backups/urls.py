from django.urls import path
from asgiref.sync import sync_to_async
from . import views

urlpatterns = [
    path('upload', sync_to_async(views.upload), name='upload'),
    path('delete/<int:pk>', views.BackupDeleteView.as_view(), name='delete'),
    path('list', views.BackupListView.as_view(), name='list'),
]
