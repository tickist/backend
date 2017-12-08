#-*- coding: utf-8 -*-
from datetime import date
from celery.task import task
from .models import Task


@task
def unsuspend_tasks():
    tasks = Task.objects.filter(status=2, is_active=True, suspend_date__lt=date.today())
    for task in tasks:
        task.status = 0
        task.save()