# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareListPending',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('is_active', models.BooleanField(default=True)),
                ('lists', models.ManyToManyField(related_name='new_shared_list', null=True, to='lists.List', blank=True)),
                ('user', models.ForeignKey(related_name='invite_another_user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
