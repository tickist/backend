# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-31 20:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0006_auto_20170322_0053'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='defaultTaskView',
            field=models.CharField(choices=[('extended', 'extended'), ('simple', 'simple')], default='extended', max_length=40),
        ),
    ]
