# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import users.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login', null=True, blank=True)),
                ('email', models.EmailField(unique=True, max_length=100, db_index=True)),
                ('username', models.CharField(unique=True, max_length=100, db_index=True)),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('date_joined', models.DateField(null=True, blank=True)),
                ('avatar', models.ImageField(default='site_media/images/default_images/default_avatar_user.png', upload_to=users.models.get_path)),
                ('is_confirm_email', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('registration_key', models.CharField(db_index=True, max_length=60, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField()),
                ('user', models.ForeignKey(related_name='user_message', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_confirm', models.BooleanField(default=True)),
                ('user1', models.ForeignKey(related_name='user1', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('user2', models.ForeignKey(related_name='user2', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user',
            name='team_mate',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='users.Team'),
            preserve_default=True,
        ),
    ]
