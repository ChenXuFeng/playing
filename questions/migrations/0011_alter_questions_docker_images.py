# Generated by Django 4.1.7 on 2023-03-16 01:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('practices', '0009_remove_dockerimages_qs'),
        ('questions', '0010_alter_questions_options_questions_docker_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='docker_images',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='qs', to='practices.dockerimages', verbose_name='docker镜像'),
        ),
    ]
