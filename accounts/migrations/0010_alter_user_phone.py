# Generated by Django 4.1.7 on 2023-02-20 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_user_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=35, unique=True, verbose_name='电话'),
        ),
    ]