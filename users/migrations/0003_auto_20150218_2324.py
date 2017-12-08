# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_daily_summary_hour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='user1',
        ),
        migrations.RemoveField(
            model_name='team',
            name='user2',
        ),
        migrations.RemoveField(
            model_name='user',
            name='team_mate',
        ),
        migrations.DeleteModel(
            name='Team',
        ),
        migrations.AddField(
            model_name='user',
            name='assigns_a_task_to_me',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='changes_a_task_from_a_shared_list_that_I_assigned_to_him_her',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='changes_a_task_from_a_shared_list_that_is_assigned_to_me',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='completes_a_task_from_a_shared_list',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='leaves_a_shared_list',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='removes_me_from_a_shared_list',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='shares_a_list_with_me',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateField(auto_now_add=True, null=True),
            preserve_default=True,
        ),
    ]
