# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0003_auto_20150207_1926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sharelistpending',
            old_name='lists1',
            new_name='lists',
        ),
    ]
