# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-28 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20170119_2321'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_task_view_today_view',
            field=models.CharField(choices=[('extended', 'extended'), ('simple', 'simple')], default='extended', max_length=40),
        ),
    ]
