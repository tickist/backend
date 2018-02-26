# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-25 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20180225_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='future_tasks_sort_by',
            field=models.CharField(choices=[('[finishDate finishTime name] [asc, desc, asc]', 'finishDate, finishTime, name'), ('[finishDate finishTime name] [asc, asc, asc]', '-finishDate, finishTime, name')], default='[finishDate finishTime name] [asc, desc, asc]', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='overdue_tasks_sort_by',
            field=models.CharField(choices=[('[priority finishDate name] [asc, desc, asc]', 'priority, finishDate, name'), ('[priority finishDate name] [asc, asc, asc]', 'priority, -finishDate, name')], default='[priority finishDate name] [asc, desc, asc]', max_length=100),
        ),
    ]
