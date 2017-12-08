# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150218_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='order_tasks_dashboard',
            field=models.CharField(default='Today->Overdue->You can do this too', max_length=40, choices=[('Today->Overdue->You can do this too', b'Today->Overdue->You can do this too'), (b'Overdue->Today->You can do this too', b'Overdue->Today->You can do this too')]),
            preserve_default=True,
        ),
    ]
