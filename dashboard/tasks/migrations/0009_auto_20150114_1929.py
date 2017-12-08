# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20141206_1157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskstep',
            options={'ordering': ['order']},
        ),
        migrations.AlterField(
            model_name='task',
            name='estimate_time',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='task',
            name='time',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'author')]),
        ),
    ]
