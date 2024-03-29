# Generated by Django 4.1.7 on 2023-03-17 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0011_alter_questions_docker_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='qs',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer', to='questions.questions', verbose_name='题库'),
        ),
        migrations.AlterField(
            model_name='answers',
            name='qs',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questions.questions', verbose_name='题库'),
        ),
    ]
