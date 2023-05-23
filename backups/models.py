import os
from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage


# Create your models here.

class MyFileStorage(FileSystemStorage):

    # This method is actually defined in Storage
    def get_available_name(self, name, max_length=None):
        # if self.exists(name):
        #     os.remove(os.path.join(settings.MEDIA_ROOT, name))
        # return name  # simply returns the name passed
        if self.exists(name):
            now = datetime.now()
            name, ext = os.path.splitext(name)
            return f"{name} at {now.strftime('%H.%M.%S')}{ext}"
        return name


customfileStorage = MyFileStorage()


class Backup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(storage=customfileStorage)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    filesize = models.IntegerField()  # store the filesize in bytes
    filesize_str = models.CharField(max_length=100, default='0 bytes')  # store the filesize as a string
    # with the appropriate unit

    def __str__(self):
        return f"{self.user.username} Backup on {self.date_uploaded.strftime('%d/%m/%Y at %H:%M')}"
