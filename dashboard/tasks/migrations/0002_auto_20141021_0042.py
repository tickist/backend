# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='estimate_time',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='repeat',
            field=models.IntegerField(default=0, choices=[[0, 'no'], [1, 'daily'], [2, 'daily (workweek)'], [3, 'weekly'], [4, 'monthly'], [5, 'yearly']]),
        ),
        migrations.AlterField(
            model_name='task',
            name='time',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
