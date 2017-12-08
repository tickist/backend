# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-15 21:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_column='this_creation_date')),
                ('send_at', models.DateTimeField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('is_send_by_S3', models.BooleanField(default=False)),
                ('is_send', models.BooleanField(default=True)),
                ('key', models.CharField(db_index=True, default='0000000000000000000000000000000000000000', max_length=60)),
                ('original_key', models.CharField(db_index=True, default='0000000000000000000000000000000000000000', max_length=60)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Sender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.EmailField(blank=True, default=False, max_length=254, null=True)),
                ('auth_sender', models.CharField(blank=True, max_length=40, null=True)),
                ('password_sender', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='email',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='emails.Sender'),
        ),
        migrations.AddField(
            model_name='email',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_from_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
