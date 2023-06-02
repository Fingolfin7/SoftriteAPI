from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    max_storage = models.IntegerField(default=(100 * pow(1024, 2)))  # store the max storage in bytes
    max_storage_str = models.CharField(max_length=100, default='0 bytes')  # store the max storage as a string
    used_storage = models.IntegerField(default=0)  # store the used storage in bytes
    used_storage_str = models.CharField(max_length=100, default='0 bytes')  # store the used storage as a string

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
