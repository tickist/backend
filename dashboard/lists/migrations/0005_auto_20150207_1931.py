# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0004_auto_20150207_1927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sharelistpending',
            old_name='lists',
            new_name='list',
        ),
    ]
