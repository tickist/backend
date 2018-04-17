# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-20 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20180226_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='overdue_tasks_sort_by',
            field=models.CharField(choices=[('{"fields": ["priority", "finishDate", "finishTime", "name"], "orders": ["asc", "asc", "asc", "asc"]}', 'priority, finishDate, name'), ('{"fields": ["priority", "finishDate", "finishTime", "name"], "orders": ["asc", "desc", "desc", "asc"]}', 'priority, -finishDate, name')], default='{"fields": ["priority", "finishDate", "finishTime", "name"], "orders": ["asc", "asc", "asc", "asc"]}', max_length=100),
        ),
    ]
