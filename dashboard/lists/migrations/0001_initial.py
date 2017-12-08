# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import dashboard.lists.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField(default='', max_length=400, null=True, blank=True)),
                ('logo', models.ImageField(default='images/default_images/default_list_logo.png', upload_to=dashboard.lists.models.get_path)),
                ('is_inbox', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('color', models.CharField(default='#2c86ff', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('default_priority', models.CharField(default='C', max_length=1, choices=[(b'A', b'A'), (b'B', b'B'), (b'C', b'C')])),
                ('default_finish_date', models.IntegerField(blank=True, max_length=25, null=True, choices=[[0, 'today'], [1, 'tomorrow'], [2, 'next week']])),
                ('default_type_finish_date', models.IntegerField(blank=True, null=True, choices=[[0, 'by'], [1, 'on']])),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('ancestor', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='lists.List', null=True, on_delete=models.DO_NOTHING)),
                ('owner', models.ForeignKey(related_name='owner_list', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('share_with', models.ManyToManyField(related_name='share_with', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
