# Generated by Django 4.1.7 on 2023-02-27 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0003_alter_answerrecords_respondent'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerrecords',
            name='notes',
            field=models.TextField(blank=True, max_length=10000, null=True, verbose_name='备注'),
        ),
    ]
