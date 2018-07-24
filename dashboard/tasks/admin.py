#-*- coding: utf-8 -*-
from django.contrib import admin
from dashboard.tasks.models import Task, TaskStatistics, TaskStep, Tag

admin.site.register(Task)
admin.site.register(TaskStatistics)
admin.site.register(TaskStep)
admin.site.register(Tag)