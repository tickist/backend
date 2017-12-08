# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0002_sharelistpending'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharelistpending',
            name='lists',
        ),
        migrations.AddField(
            model_name='sharelistpending',
            name='lists1',
            field=models.ForeignKey(blank=True, to='lists.List', null=True, on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
    ]
