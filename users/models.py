from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    website = models.URLField(max_length=200, blank=True)
    logo = models.ImageField(default='default_logo.png', upload_to='company_logos')

    max_storage = models.IntegerField(default=(100 * pow(1024, 2)))  # store the max storage in bytes
    used_storage = models.IntegerField(default=0)  # store the used storage in bytes

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.logo.path)
        if img.height > 100 or img.width > 100:
            output_size = (100, 100)
            img.thumbnail(output_size)
            img.save(self.logo.path)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    is_company_admin = models.BooleanField(default=False)  # company admin can add users to the company
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    firstname = models.CharField(max_length=100, default='', blank=True)
    lastname = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=15, default='', blank=True)
    # email = models.EmailField(max_length=254) # this is already in the User model

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
