# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-01 21:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_user_all_tasks_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='projects_filter_id',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='user',
            name='tags_filter_id',
            field=models.IntegerField(default=1),
        ),
    ]
