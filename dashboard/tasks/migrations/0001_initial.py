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
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='this_creation_date')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('priority', models.CharField(default='C', max_length=1, db_index=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])),
                ('description', models.TextField(null=True, blank=True)),
                ('estimate_time', models.IntegerField(null=True, blank=True)),
                ('time', models.IntegerField(null=True, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='this_creation_date')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('finish_date', models.DateField(null=True, blank=True)),
                ('finish_time', models.TimeField(null=True, blank=True)),
                ('type_finish_date', models.IntegerField(blank=True, null=True, choices=[[0, 'by'], [1, 'on']])),
                ('percent', models.IntegerField(default=0)),
                ('repeat', models.IntegerField(default=0, choices=[[0, 'no'], [1, 'daily'], [2, 'daily (work week)'], [3, 'weekly'], [4, 'monthly'], [5, 'yearly']])),
                ('repeat_delta', models.IntegerField(default=1)),
                ('from_repeating', models.IntegerField(default=0, choices=[[0, 'completion date'], [1, 'due date']])),
                ('status', models.IntegerField(default=0, choices=[[0, 'is undone'], [1, 'is done'], [2, 'is suspended']])),
                ('when_complete', models.DateTimeField(null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('suspend_date', models.DateField(null=True, blank=True)),
                ('ancestor', models.ForeignKey(related_name='self', blank=True, to='tasks.Task', null=True, on_delete=models.CASCADE)),
                ('author', models.ForeignKey(related_name='author', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('owner', models.ForeignKey(related_name='owner', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('tags', models.ManyToManyField(to='tasks.Tag', null=True, blank=True)),
                ('task_list', models.ForeignKey(blank=True, to='lists.List', null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estimate_time_sum', models.IntegerField(default=0)),
                ('spend_time_sum', models.IntegerField(default=0)),
                ('date', models.DateField(db_index=True)),
                ('tasks_counter', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='this_creation_date')),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(default=0, choices=[[0, 'is undone'], [1, 'is done']])),
                ('order', models.PositiveIntegerField(default=100)),
                ('author', models.ForeignKey(related_name='step_author', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('owner', models.ForeignKey(related_name='user_last_change', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('task', models.ForeignKey(to='tasks.Task', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
