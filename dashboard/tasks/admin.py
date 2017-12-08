#-*- coding: utf-8 -*-
from django.contrib import admin
from dashboard.tasks.models import Task

admin.site.register(Task)