# Generated by Django 4.1.7 on 2023-03-16 01:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('practices', '0008_rename_imagename_dockerimages_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dockerimages',
            name='qs',
        ),
    ]
