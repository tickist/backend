# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_order_tasks_dashboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='deletes_a_list_shared_with_me',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
