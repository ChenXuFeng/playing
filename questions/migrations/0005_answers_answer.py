# Generated by Django 4.1.7 on 2023-03-09 05:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_remove_questions_answer_remove_questions_answers_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(default='', max_length=512, verbose_name='值')),
                ('qs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questions.questions', verbose_name='题库')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(default='', max_length=512, verbose_name='值')),
                ('qs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer', to='questions.questions', verbose_name='题库')),
            ],
        ),
    ]
