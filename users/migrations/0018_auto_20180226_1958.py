# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-26 18:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20180226_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='future_tasks_sort_by',
            field=models.CharField(choices=[('{"fields": ["finishDate", "finishTime", "name"], "orders": ["desc", "asc", "asc"]}', 'finishDate, finishTime, name'), ('{"fields": ["finishDate", "finishTime", "name"], "orders": ["asc", "desc", "asc"]}', '-finishDate, finishTime, name')], default='{"fields": ["finishDate", "finishTime", "name"], "orders": ["desc", "asc", "asc"]}', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='overdue_tasks_sort_by',
            field=models.CharField(choices=[('{"fields": ["priority", "finishDate", "name"], "orders": ["asc", "asc", "asc"]}', 'priority, finishDate, name'), ('{"fields": ["priority", "finishDate", "name"], "orders": ["asc", "desc", "asc"]}', 'priority, -finishDate, name')], default='{"fields": ["priority", "finishDate", "name"], "orders": ["asc", "asc", "asc"]}', max_length=100),
        ),
    ]
