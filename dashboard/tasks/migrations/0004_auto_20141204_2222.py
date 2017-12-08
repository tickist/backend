# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20141023_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='pinned',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='taskstep',
            name='task',
            field=models.ForeignKey(related_name='steps', to='tasks.Task', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
