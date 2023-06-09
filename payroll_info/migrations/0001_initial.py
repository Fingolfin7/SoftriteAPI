# Generated by Django 3.2.9 on 2023-03-21 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InterbankUSDRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('rate', models.FloatField()),
            ],
            options={
                'verbose_name_plural': 'Interbank USD Rates',
            },
        ),
    ]
