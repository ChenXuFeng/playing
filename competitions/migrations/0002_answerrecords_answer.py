# Generated by Django 4.1.7 on 2023-02-22 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerrecords',
            name='answer',
            field=models.CharField(default=None, max_length=32, verbose_name='答案'),
            preserve_default=False,
        ),
    ]