# Generated by Django 4.2 on 2023-06-06 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_max_storage_profile_max_storage_str_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='max_storage_str',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='used_storage_str',
        ),
    ]
