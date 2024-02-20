import os
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from users.models import Profile, Company


class MyFileStorage(FileSystemStorage):
    # This method is actually defined in the Storage class
    def get_available_name(self, name, max_length=None):
        # if self.exists(name):
        #     os.remove(os.path.join(settings.MEDIA_ROOT, name))
        # return name  # simply returns the name passed
        if self.exists(name):
            now = datetime.now().strftime('%m-%d-%Y at %H.%M.%S')
            name, ext = os.path.splitext(name)
            return f"{name} ({now}){ext}"
        return name


customFileStorage = MyFileStorage()


class Backup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    file = models.FileField(storage=customFileStorage)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    filesize = models.IntegerField()  # store the filesize in bytes

    def __str__(self):
        return f"{self.company.name} Backup on {self.date_uploaded.strftime('%m-%d-%Y at %H:%M')}" \
               f" by {self.user.username}"

    class Meta:
        ordering = ["-date_uploaded"]

    @property
    def basename(self):
        return os.path.basename(self.file.name)

    @property
    def adaski_path(self):
        # return the filepath of the backup but remove the MEDIA_ROOT from the beginning
        return os.path.dirname(self.file.path).replace(
            os.path.join(os.getcwd(), os.path.normpath('media/backups/')), '')

    def save(self, *args, **kwargs):
        self.filesize = self.file.size

        self.company.used_storage += self.filesize
        self.company.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.company.used_storage >= self.filesize:
            self.company.used_storage -= self.filesize
        else:
            self.company.used_storage = 0

        self.company.save()

        # this ended up being unnecessary because I'm using django-cleanup to automatically delete files
        # when the model is deleted
        """# check if file exists before deleting
        if hasattr(self.file, 'storage') and self.file.storage.exists(self.file.name):
            self.file.delete()"""

        super().delete(*args, **kwargs)


class Comment(models.Model):
    backup = models.ForeignKey(Backup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    # allows for replies to comments
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created.strftime('%m-%d-%Y at %H:%M')}"
