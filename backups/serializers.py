import os
from .models import Backup
from django.utils import timezone
from rest_framework import serializers


class BackupSerializer(serializers.ModelSerializer):
    date_uploaded = serializers.DateTimeField(format="%m-%d-%Y")
    time = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    savepath = serializers.SerializerMethodField()

    class Meta:
        model = Backup
        fields = ['id', 'user', 'company', 'file', 'date_uploaded', 'time', 'filesize', 'savepath']

    def get_file(self, obj):
        return os.path.basename(obj.file.name)

    def get_time(self, obj):
        # return the time the backup was uploaded in the format "%H:%M" and in the user's timezone
        return timezone.localtime(obj.date_uploaded).strftime("%H:%M")

    def get_user(self, obj):
        return obj.user.username

    def get_company(self, obj):
        return obj.company.name

    def get_savepath(self, obj):
        path = obj.adaski_path.replace(obj.company.name + os.path.sep, '')  # remove the company name from the path
        # remove the starting slash from the path if it's still there
        if path.startswith(os.path.sep):
            path = path[1:]

        return path
