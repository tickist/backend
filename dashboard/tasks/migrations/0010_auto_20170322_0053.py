# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-21 23:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20150114_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], db_index=True, default='C', max_length=1),
        ),
        migrations.AlterField(
            model_name='task',
            name='tags',
            field=models.ManyToManyField(blank=True, to='tasks.Tag'),
        ),
    ]