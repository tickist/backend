#-*- coding: utf-8 -*-
from datetime import date

from .models import Task


class FiltersTagMixin(object):

    def _check_tags_owner(self, tags, all_ids_list):
        filtered_task_list = []
        for tag in tags:
            if tag['id'] in all_ids_list:
                filtered_task_list.append(tag)
        return filtered_task_list

    def _filters_tags(self, data, all_ids_list):
        if isinstance(data, dict):
            data['tags'] = self._check_tags_owner(data['tags'], all_ids_list) if 'tags' in data and data['tags'] else []
        elif isinstance(data, list):
            for task in data:
                task['tags'] = self._check_tags_owner(task['tags'], all_ids_list) if 'tags' in task and task['tags'] else []

        return data

# @task
def unsuspend_tasks():
    tasks = Task.objects.filter(status=2, is_active=True, suspend_date__lt=date.today())
    for task in tasks:
        task.status = 0
        task.save()
