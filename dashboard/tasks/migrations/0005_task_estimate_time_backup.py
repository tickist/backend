# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20141204_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='estimate_time_backup',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='time_backup',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
