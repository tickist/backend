# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_auto_20141206_1157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='estimate_time_backup',
            new_name='estimate_time',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='time_backup',
            new_name='time',
        ),
        migrations.AlterField(
            model_name='task',
            name='time',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
