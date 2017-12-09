# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='daily_summary_hour',
            field=models.TimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]