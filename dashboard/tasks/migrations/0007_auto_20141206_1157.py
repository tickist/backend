# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_auto_20141206_1155'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='estimate_time',
        ),
        migrations.RemoveField(
            model_name='task',
            name='time',
        )
    ]
