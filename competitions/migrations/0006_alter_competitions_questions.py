# Generated by Django 4.1.7 on 2023-03-14 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0009_rename_delete_questions_is_delete'),
        ('competitions', '0005_answerrecords_gid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitions',
            name='questions',
            field=models.ManyToManyField(blank=True, related_name='cometitions', to='questions.questions', verbose_name='题库'),
        ),
    ]