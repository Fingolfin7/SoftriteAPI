import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from users.models import Profile


def convert_size(size_bytes: int) -> str:
    """ Takes a file size in bytes and returns a string with the appropriate unit.
    E.g. 1024 bytes -> 1 KB  or 1024 MB -> 1 GB
    """
    if size_bytes == 0:
        return '0 bytes'
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f'{size_bytes:.2f} {unit}'
        size_bytes /= 1024


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


customFileStorage = MyFileStorage()


class Backup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(storage=customFileStorage)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    filesize = models.IntegerField()  # store the filesize in bytes
    filesize_str = models.CharField(max_length=100, default='0 bytes')  # store the filesize as a string

    def __str__(self):
        return f"{self.user.username} Backup on {self.date_uploaded.strftime('%d/%m/%Y at %H:%M')}"

    @property
    def basename(self):
        return os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        self.filesize = self.file.size
        self.filesize_str = convert_size(self.filesize)

        user_profile = Profile.objects.get(user=self.user)
        user_profile.used_storage += self.filesize
        user_profile.used_storage_str = convert_size(self.filesize)
        user_profile.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.user)
        user_profile.used_storage -= self.filesize
        user_profile.used_storage_str = convert_size(user_profile.used_storage)
        user_profile.save()

        self.file.delete()

        super().delete(*args, **kwargs)
