# Generated by Django 4.1.7 on 2023-02-28 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dockerimages',
            name='cport',
            field=models.IntegerField(default=0, verbose_name='容器端口'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dockerimages',
            name='notes',
            field=models.CharField(default='', max_length=2048, verbose_name='说明'),
            preserve_default=False,
        ),
    ]