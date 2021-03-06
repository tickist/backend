# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 21:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_user_default_task_view_today_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_task_view',
            field=models.CharField(choices=[('extended', 'extended'), ('simple', 'simple')], default='extended', max_length=40),
        ),
        migrations.AddField(
            model_name='user',
            name='default_task_view_future_view',
            field=models.CharField(choices=[('extended', 'extended'), ('simple', 'simple')], default='simple', max_length=40),
        ),
        migrations.AddField(
            model_name='user',
            name='default_task_view_overdue_view',
            field=models.CharField(choices=[('extended', 'extended'), ('simple', 'simple')], default='extended', max_length=40),
        ),
        migrations.AddField(
            model_name='user',
            name='default_task_view_tags_view',
            field=models.CharField(choices=[('extended', 'extended'), ('simple', 'simple')], default='extended', max_length=40),
        ),
    ]
