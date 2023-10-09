import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image, ImageSequence


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
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone = models.CharField(max_length=15, default='', blank=True)
    is_company_admin = models.BooleanField(default=False)  # company admin can add users to the company
    get_backup_emails = models.BooleanField(default=True)  # whether to get backup emails or not

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image)

        if img.format == 'GIF':
            # trying to trigger the save method of the image field so that django_cleanups can clean up the old image
            self.image = self.resize_gif(img)

        elif img.format != 'GIF' and (img.height > 450 or img.width > 450):
            img_width = img.size[0] if img.size[0] < 450 else 450
            img_height = img.size[1] if img.size[1] < 450 else 450

            output_size = (img_width, img_height)
            img.thumbnail(output_size, Image.ANTIALIAS)
            img.save(self.image.path)


    def resize_gif(self, img):
        """
        Resize a gif image by resizing each frame and then reassembling the frames into a new gif
        """

        frame_width = img.size[0] if img.size[0] < 450 else 450
        frame_height = img.size[1] if img.size[1] < 450 else 450

        if frame_width == img.size[0] and frame_height == img.size[1]: # if the image is already the correct size
            return self.image

        frames = []
        durations = []  # Store frame durations
        disposal_methods = []  # Store disposal methods

        for frame in ImageSequence.Iterator(img):
            # Resize the frame
            frame = frame.resize((frame_width, frame_height), Image.ANTIALIAS)

            # Extract and store the frame duration and disposal method
            durations.append(frame.info.get("duration", 100))  # Default duration is 100 ms
            disposal_methods.append(frame.info.get("disposal_method", 0))  # Default disposal method is 0

            frames.append(frame)

        # Create a new GIF with frame durations and disposal methods
        with BytesIO() as output_buffer:
            frames[0].save(
                output_buffer,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                disposal=disposal_methods,
                loop=img.info.get("loop", 0)  # Copy the loop count from the original
            )

            buffer = BytesIO(output_buffer.getvalue())

        return InMemoryUploadedFile(
            buffer,
            'ImageField',
            os.path.normpath(self.image.path),
            'image/gif',
            buffer.getbuffer().nbytes,
            None
        )
