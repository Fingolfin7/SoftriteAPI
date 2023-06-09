# Generated by Django 4.2 on 2023-06-01 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='max_storage',
            field=models.IntegerField(default=104857600),
        ),
        migrations.AddField(
            model_name='profile',
            name='max_storage_str',
            field=models.CharField(default='0 bytes', max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='used_storage',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='used_storage_str',
            field=models.CharField(default='0 bytes', max_length=100),
        ),
    ]
