# Generated by Django 4.1.7 on 2023-03-15 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0006_alter_competitions_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerrecords',
            name='handed',
            field=models.BooleanField(default=False, verbose_name='交卷'),
        ),
    ]