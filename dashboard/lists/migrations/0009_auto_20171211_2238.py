# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-11 21:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0008_auto_20171120_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner_list', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='sharelistpending',
            name='list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lists.List'),
        ),
    ]