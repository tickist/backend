# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-11 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20181011_0242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='future_tasks_sort_by',
            field=models.CharField(choices=[('{"fields": ["finishDate", "finishTime", "name"], "orders": ["desc", "asc", "asc"]}', 'finishDate, finishTime, name'), ('{"fields": ["priority", "finishDate", "finishTime", "name"], "orders": ["asc", "desc", "asc", "asc"]}', 'priority, finishDate, finishTime, name'), ('{"fields": ["finishDate", "finishTime", "name"], "orders": ["asc", "desc", "asc"]}', '-finishDate, finishTime, name')], default='{"fields": ["finishDate", "finishTime", "name"], "orders": ["desc", "asc", "asc"]}', max_length=200),
        ),
    ]
