# Generated by Django 4.2.2 on 2023-09-11 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backups', '0006_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='backup',
            options={'ordering': ['-date_uploaded']},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created']},
        ),
    ]
