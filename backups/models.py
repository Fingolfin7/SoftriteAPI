import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from users.models import Profile


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

    def __str__(self):
        return f"{self.user.username} Backup on {self.date_uploaded.strftime('%d/%m/%Y at %H:%M')}"

    @property
    def basename(self):
        return os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        self.filesize = self.file.size

        user_profile = Profile.objects.get(user=self.user)
        user_profile.used_storage += self.filesize
        user_profile.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user_profile = Profile.objects.get(user=self.user)

        if user_profile.used_storage >= self.filesize:
            user_profile.used_storage -= self.filesize
        else:
            user_profile.used_storage = 0

        user_profile.save()

        # this ended up being unnecessary because I'm using django-cleanup to delete files
        # when the model is deleted automatically
        """# check if file exists before deleting
        if hasattr(self.file, 'storage') and self.file.storage.exists(self.file.name):
            self.file.delete()"""

        super().delete(*args, **kwargs)
