import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class UpdateTaskMixin():

    def _update_task(self, task):
        url = reverse("task-detail", kwargs={"pk": task.id})
        suspend_date = task.suspend_date.strftime('%d-%m-%Y') if task.suspend_date else None
        response = self.client.put(url, json.dumps({"repeat": task.repeat, "description": task.description,
                                                     "finish_date": task.finish_date.strftime('%d-%m-%Y'),
                                                     "percent": task.percent, "estimate_time": task.estimate_time,
                                                     "creation_date": task.creation_date.isoformat(),
                                                     "type_finish_date": task.type_finish_date,
                                                     "owner": task.owner.pk, "name": task.name,
                                                     "modification_date": task.modification_date.isoformat(),
                                                     "author": task.author.pk, "status": task.status,
                                                     "priority": task.priority, "task_project": task.task_list.pk,
                                                     "time": task.time, "ancestor": task.ancestor,
                                                     "suspend_date": suspend_date,
                                                     "from_repeating": task.from_repeating, "repeat_delta":
                                                    task.repeat_delta, "is_active": True})
                , follow=True, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return json.loads(response.content.decode("utf-8"))
