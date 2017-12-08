# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(default='{}')),
                ('codename', models.CharField(max_length=250)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='this_creation_date')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('object_id', models.PositiveIntegerField()),
                ('type', models.CharField(default='email', max_length=50, db_index=True,
                                           choices=[('email', 'email'), ('web', 'web')])),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='this_creation_date')),
                ('is_read', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
                ('notification_content', models.ForeignKey(to='notifications.NotificationContent', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
