# Generated by Django 4.1.7 on 2023-04-04 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practices', '0010_alter_dockerimages_imageid'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockercontainers',
            name='flag',
            field=models.CharField(blank=True, default='', max_length=128, null=True),
        ),
    ]
