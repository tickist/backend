#-*- coding: utf-8 -*-

from django.test import LiveServerTestCase
#from selenium.webdriver.firefox.webdriver import WebDriver
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.translation import ugettext as _
from dashboard.tasks.models import Task, TaskStep, TaskStatistics
from dashboard.lists.models import List
from users.factory_classes import UserFactory
from dashboard.lists.factory_classes import ListFactory, ListFactoryShareWithUsers
from dashboard.tasks.factory_classes import TaskFactory, TaskWithStepsFactory, TagFactory, TaskWithTagsAndStepsFactory
from dashboard.tasks.serializers import TaskSerializer
from users.models import User
from rest_framework import status
from django.db.models import Q
import json
from datetime import date, timedelta
from rest_framework.renderers import JSONRenderer
from dateutil.relativedelta import relativedelta
from .mixins import UpdateTaskMixin


class CreateTaskTest(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def test_simply_create_task(self):
        task_name = "Task 1"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({"name": task_name, 'task_project': self.john.inbox_pk}), follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.owner.pk, self.john.pk)
        self.assertEqual(task.name, task_name)
        self.assertEqual(task.percent, 0)
        self.assertEqual(task.priority, "C")


    def test_simply_create_task_with_empty_step_key(self):
        """
        Issue #159
        """
        task_name = "Task 1"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({"name": task_name, 'task_project': self.john.inbox_pk, 'steps':[]}), follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.owner.pk, self.john.pk)
        self.assertEqual(task.name, task_name)
        self.assertEqual(task.percent, 0)
        self.assertEqual(task.priority, "C")

    def test_simpty_create_task_some_attribute_with_null_values(self):
        task_name = "Task 1"
        task_estimate_time = 111
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': task_estimate_time,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': None,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.owner.pk, self.john.pk)
        self.assertEqual(task.name, task_name)
        self.assertEqual(task.percent, 0)
        self.assertEqual(task.type_finish_date, 1)
        self.assertEqual(task.estimate_time, task_estimate_time)
        self.assertEqual(task.priority, "C")
        self.assertEqual(task.task_list.pk, 1)


class CleateTaskDifferentOwnerAuthor(TestCase):
    """


    """
    def setUp(self):
        self.url = reverse("task-list")
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()
        self.enemy = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.user1)
        self.list_1.share_with.add(self.user2)
        self.list_1.share_with.add(self.user3)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.user1.email, password="pass"))

    def test_create_task_different_owner(self):
        url = reverse("task-list")
        task_name = "Test task"
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': self.user2.pk,
                                                     u'name': task_name, u'modification_date': None, u'author': self.user1.pk,
                                                     u'status': 0, u'priority': None, u'task_project': self.list_1.pk,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.owner, self.user2)
        self.assertEqual(task.author, self.user1)

    def test_create_task_new_owner_is_not_in_the_team(self):
        url = reverse("task-list")
        task_name = "Test task"
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': self.enemy.pk,
                                                     u'name': task_name, u'modification_date': None, u'author': self.user1.pk,
                                                     u'status': 0, u'priority': None, u'task_project': self.list_1.pk,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_bad_author(self):
        """
            User1 is loggin but we try to set author == self.user2.pk
        """
        url = reverse("task-list")
        task_name = "Test task"
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': self.user2.pk,
                                                     u'name': task_name, u'modification_date': None, u'author': self.user2.pk,
                                                     u'status': 0, u'priority': None, u'task_project': self.list_1.pk,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.owner, self.user2)
        self.assertEqual(task.author, self.user1)

    def test_create_task_owner_is_none(self):

        url = reverse("task-list")
        task_name = "Test task"
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'owner': None,
                                                     u'creation_date': None, u'type_finish_date': 0,
                                                     u'name': task_name, u'modification_date': None, u'author': self.user1.pk,
                                                     u'status': 0, u'priority': None, u'task_project': self.list_1.pk,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.owner, self.user1)
        self.assertEqual(task.author, self.user1)

class CreateTaskWithTimeTest(TestCase):
    """
        Create task with time and estimate time in specal format (e.g. 2h 34m)
    """

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def test_time_without_space(self):
        task_name = "Task 1"
        task_estimate_time = "2h12m"
        task_time = "12m "
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': task_estimate_time,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': task_time,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.estimate_time, 132)
        self.assertEqual(task.time, 12)

    def test_time(self):
        task_name = "Task 1"
        task_estimate_time = "2d 2h 12m"
        task_time = "12"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': task_estimate_time,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': task_time,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.estimate_time, 3012)
        self.assertEqual(task.time, 12)

    def test_tricky_time(self):
        task_name = "Task 1"
        task_estimate_time = "23Km" #"K" is ignored
        task_time = "21KK 12mmd"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': task_estimate_time,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': task_time,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.estimate_time, 23)
        self.assertEqual(task.time, 21)

    def test_tricky_time_2(self):
        task_name = "Task 1"
        task_estimate_time = "NaNh NaNm"
        task_time = "21KK 12mmd"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': task_estimate_time,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': task_time,
                                                     u'ancestor': None}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(name=task_name)
        self.assertEqual(task.estimate_time, 0)


class EditTaskTest(TestCase):

    def setUp(self):
        self.john = UserFactory.create(username="john", email="john@example.com")
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        self.list_1 = ListFactory.create(owner=self.john)

    def _update_task(self, task):
        url = reverse("task-detail", kwargs={"pk": task.id})
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
                                                     "suspend_date": task.suspend_date.strftime('%d-%m-%Y'),
                                                     "from_repeating": task.from_repeating, "repeat_delta":
                                                    task.repeat_delta, "is_active": True})
                , follow=True, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return json.loads(response.content.decode('utf-8'))

    def _check_tasks(self, task_from_database, task_from_response):
        self.assertEqual(task_from_database, task_from_response)

    def test_suspend_date_and_status(self):
        task = TaskFactory.create(owner=self.john, author=self.john, task_list=self.list_1, status=0, priority="A")
        task.suspend_date = date.today()
        task.status = 1
        updated_task = self._update_task(task)
        task_from_database = Task.objects.get(id=task.pk)
        self.assertEqual(task_from_database.suspend_date, None)

    def test_delete_task_pass(self):
        task = TaskFactory.create(owner=self.john, author=self.john, task_list=self.list_1, status=0, priority="A")
        url = reverse("task-detail", kwargs={'pk': task.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deleted_task = Task.objects.get(id=task.pk)
        self.assertFalse(deleted_task.is_active)

    def test_delete_task_not_permission(self):
        not_john = UserFactory.create(username="not_john", email="not_john@example.com")
        task = TaskFactory.create(owner=self.john, author=not_john, task_list=self.list_1, status=0, priority="A")
        self.assertTrue(self.client.login(email=not_john.email, password="pass"))
        url = reverse("task-detail", kwargs={'pk': task.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        deleted_task = Task.objects.get(id=task.pk)
        self.assertTrue(deleted_task.is_active)


class RepeatingTaskTest(TestCase):
    """
    Testing repeating options after task is done
    """

    def setUp(self):
        self.user = UserFactory.create()
        self.user_inbox = List.objects.get(id=self.user.inbox_pk)
        self.assertTrue(self.client.login(email=self.user.email, password="pass"))

    def _serialize_task(self, task):
        """
        This function return json
        """
        task_serialized = TaskSerializer(task)
        task_json = task_serialized.data.copy()
        task_json['task_project'] = task_json['task_project']["id"]
        if task_serialized.data['finish_date']:
          list_date_tmp = task_json['finish_date'].split("-")
          task_json['finish_date'] = "{}-{}-{}T23:00:00.000Z".format(list_date_tmp[2], list_date_tmp[1], list_date_tmp[0])
       
        json = JSONRenderer().render(task_json)
        return json

    def test_repeat_every_day_from_completion(self):
        """
            Repeating task every day from completion
        """

        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=1, finish_date=None)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id = task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(date.today() + relativedelta(days=1), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_day_from_due_date(self):
        """
            Repeating task every day from completion
        """
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=1, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(days=1), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_day_workweek_from_completion(self):
        """
            Repeating task every day from due date (only workweek)
        """

        finish_date = date(2013, 10, 11) #it is friday
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=2, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(days=3), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_day_workweek_from_due_date(self):
        """
            Repeating task every day from dued ate (only workweek)
        """
        finish_date = date(2013, 10, 12) #it is saturnday
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=2, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(days=2), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_six_day_workweek_from_due_date(self):
        """
            Repeating task every day from dued ate (only workweek)
        """
        finish_date = date(2013, 10, 12) #it is saturday
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=2, finish_date=finish_date, from_repeating=1)
        task.status = 1
        task.repeat_delta = 6
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(days=9), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_week_from_completion(self):
        """
            Repeating task every day from completion
        """

        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=3, finish_date=None)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(date.today() + relativedelta(days=7), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_week_from_due_date(self):
        """
            Repeating task every day from completion
        """
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=3, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id = task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(days=7), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_three_week_from_due_date(self):
        """
            Repeating task every day from completion
        """
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=3, finish_date=finish_date, from_repeating=1)
        task.status = 1
        task.repeat_delta = 3
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(days=21), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_month_from_completion(self):
        """
            Repeating task every day from completion
        """

        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=4, finish_date=None)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id = task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(date.today() + relativedelta(months=1), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_two_month_from_completion(self):
        """
            Repeating task every day from completion
        """

        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=4, finish_date=None)
        task.status = 1
        task.repeat_delta = 2
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id = task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(date.today() + relativedelta(months=2), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_month_from_due_date(self):
        """
            Repeating task every day from completion
        """
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=4, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True, content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(months=1), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_year_from_completion(self):
        """
            Repeating task every day from completion
        """

        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", task_list=self.user_inbox,
                                  repeat=5, finish_date=None)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task), follow=True,
                                   content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(date.today() + relativedelta(years=1), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_every_year_from_due_date(self):
        """
            Repeating task every day from completion
        """
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A",
                                  task_list=self.user_inbox, repeat=5, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True,  content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(years=1), task.finish_date)
        self.assertEqual(0, task.status)

    def test_repeat_pinned_tasks(self):
        """
            Repeating task every day from completion
        """
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.user, author=self.user, status=0, priority="A", pinned=True,
                                  task_list=self.user_inbox, repeat=5, finish_date=finish_date, from_repeating=1)
        task.status = 1
        response = self.client.put(reverse("task-detail", kwargs={"pk": task.pk}), self._serialize_task(task),
                                   follow=True,  content_type='application/json')
        task = Task.objects.get(id=task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(finish_date + relativedelta(years=1), task.finish_date)
        self.assertEqual(0, task.status)
        self.assertEqual(False, task.pinned)



class CreateTaskWithSteps(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def test_simply_create_task(self):
        task_name = "Task 1"
        url = reverse("task-list")
        steps_name = [u"Step #1", u"Step #2"]
        steps = {
            'steps-TOTAL_FORMS': u'2',
            'steps-INITIAL_FORMS': u'0',
            'steps-MAX_NUM_FORMS': u'2',
            'steps-0-name': steps_name[0],
            'steps-0-order': u'0',
            'steps-1-name': steps_name[1],
            'steps-1-order': u'1',

        }
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': 111,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': None,
                                                     u'ancestor': None, u"steps": steps}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.owner.pk, self.john.pk)
        self.assertEqual(task.name, task_name)
        self.assertEqual(task.percent, 0)
        self.assertEqual(task.priority, "C")
        for i, step in enumerate(TaskStep.objects.filter(task=task)):
            self.assertEqual(step.name, steps_name[i])
            self.assertEqual(step.task.id, task.id)
            self.assertEqual(step.author.id, self.john.id)
            self.assertEqual(step.owner.id, self.john.id)


class EditTaskWithSteps(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        for _ in range(1):
            self.task1 = TaskWithStepsFactory.create(task_list=List.objects.get(id=self.john.inbox_pk), owner=self.john,
                                        author=self.john, finish_date=None)

    def _update_task(self, task, steps):
        url = reverse("task-detail", kwargs={"pk": task.id})
        response = self.client.put(url, json.dumps({"repeat": task.repeat, "description": task.description,
                                                    "percent": task.percent, "estimate_time": task.estimate_time,
                                                     "creation_date": task.creation_date.isoformat(),
                                                     "type_finish_date": task.type_finish_date,
                                                     "owner": task.owner.pk, "name": task.name,
                                                     "modification_date": task.modification_date.isoformat(),
                                                     "author": task.author.pk, "status": task.status,
                                                     "priority": task.priority, "task_project": task.task_list.pk,
                                                     "time": task.time, "ancestor": task.ancestor,
                                                     "from_repeating": task.from_repeating, "steps":steps,
                                                     'repeat_delta': task.repeat_delta, "is_active": True}),
                                   follow=True, content_type="application/json")
        return response

    def _create_steps_dict(self, task):
        steps = {}
        for i, one_step in enumerate(TaskStep.objects.filter(task=task)):
            steps["steps-%d-name" % i] = one_step.name
            steps["steps-%d-status" % i] = one_step.status
            steps["steps-%d-order" % i] = one_step.order
            steps["steps-%d-id" % i] = one_step.id
            steps["steps-%d-task" % i] = task.id
        steps['steps-TOTAL_FORMS'] = TaskStep.objects.filter(task=task).count()
        steps['steps-INITIAL_FORMS'] = TaskStep.objects.filter(task=task).count()
        steps['steps-MAX_NUM_FORMS'] = u""
        return steps
      
    def test_change_status_and_name_steps(self):
        task = Task.objects.get(id=self.task1.id)
        steps = self._create_steps_dict(task)
        steps.update({'steps-3-status': u"1"})
        steps.update({'steps-4-status': u"1"})
        steps.update({'steps-3-name': u"NEW NAME"})
        steps.update({'steps-4-name': u"NEW NAME"})
        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)

        step3 = TaskStep.objects.get(id=steps["steps-3-id"])
        step4 = TaskStep.objects.get(id=steps["steps-4-id"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(step3.status, 1)
        self.assertEqual(step4.status, 1)
        self.assertEqual(step3.name, "NEW NAME")
        self.assertEqual(step4.name, "NEW NAME")
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 5)

    def test_edit_steps_errors(self):
        task = Task.objects.get(id=self.task1.id)
        steps = self._create_steps_dict(task)
        steps.update({'steps-3-status': u""})
        steps.update({'steps-4-status': u"1"})
        steps.update({'steps-3-name': u"NEW NAME"})
        steps.update({'steps-4-name': u"NEW NAME"})
        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 5)
        steps = self._create_steps_dict(task)
        steps.update({'steps-3-status': u"1"})
        steps.update({'steps-4-status': u"1"})
        steps.update({'steps-3-name': u""})
        steps.update({'steps-4-name': u"NEW NAME"})
        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #nothing change
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 5)

    def test_add_new_steps(self):
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 5)
        steps = self._create_steps_dict(task)
        steps['steps-5-name'] = u"New step"
        steps['steps-5-order'] = u"7"
        steps['steps-5-status'] = u"0"
        steps['steps-5-task'] = task.id
        steps.update({'steps-TOTAL_FORMS': 6})
        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)
        step6 = TaskStep.objects.get(id=6)
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 6)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(step6.status, 0)
        self.assertEqual(step6.task.id, self.task1.id)
        self.assertEqual(step6.name, "New step")

    def test_delete_new_steps(self):
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 5)
        steps = self._create_steps_dict(task)
        steps['steps-3-DELETE'] = "steps-3-DELETE"
        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 4)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TaskStep.objects.filter(id=steps['steps-3-id']).count(), 0)

    def test_change_percent_after_change_step_status(self):
        task = Task.objects.get(id=self.task1.id)
        steps = self._create_steps_dict(task)
        steps.update({'steps-3-status': u"1"})
        response = self._update_task(task, steps)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)

        step3 = TaskStep.objects.get(id=steps["steps-3-id"])
        self.assertEqual(step3.status, 1)
        self.assertEqual(task.percent, 20)
        self.assertEqual(TaskStep.objects.filter(task=task).count(), 5)

        steps.update({'steps-2-status': u"1"})
        response = self._update_task(task, steps)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.percent, 40)

        steps.update({'steps-3-status': u"0"})
        response = self._update_task(task, steps)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.percent, 20)

    def test_done_task_after_done_all_steps(self):
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.status, 0)
        steps = self._create_steps_dict(task)
        steps.update({'steps-0-status': u"1"})
        steps.update({'steps-1-status': u"1"})
        steps.update({'steps-2-status': u"1"})
        steps.update({'steps-3-status': u"1"})
        steps.update({'steps-4-status': u"1"})
        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(task.percent, 100)
        self.assertEqual(task.status, 1)

    def test_undone_task_after_undone_one_step(self):
        #prepare data
        task = Task.objects.get(id=self.task1.id)
        task.status = 1
        task.save()
        TaskStep.objects.all().update(status=1)
        self.assertEqual(task.status, 1)
        steps = self._create_steps_dict(task)
        steps.update({'steps-0-status': u"0"})

        response = self._update_task(task, steps)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.status, 0)

    def test_done_all_steps_after_done_task(self):
        task = Task.objects.get(id=self.task1.id)
        task.status = 1
        response = self._update_task(task, self._create_steps_dict(task))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)
        for step in TaskStep.objects.filter(task=task):
            self.assertEqual(step.status, 1)

    def test_done_task_with_steps_with_repeating_options(self):
        task = Task.objects.get(id=self.task1.id)
        task.repeat = 2
        task.repeat_delta = 2
        task.from_repeating = 0
        task.save()
        TaskStep.objects.filter(task=task)[0].status = 1
        TaskStep.objects.filter(task=task)[0].save()
        task = Task.objects.get(id=self.task1.id)
        task.status = 1
        task.save()
        response = self._update_task(task, self._create_steps_dict(task))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.status, 0)
        for step in TaskStep.objects.filter(task=task):
            self.assertEqual(step.status, 0)

    def test_done_task_with_steps_with_repeating_options_2(self):
        """
            Zmieniam wszystkie stepy na done wtedy zadanie i stepy powinny być na undone i
            zadanie powinno mieć nową datę ukończenia
        """
        task = Task.objects.get(id=self.task1.id)
        task.repeat = 2
        task.repeat_delta = 2
        task.from_repeating = 0
        task.save()
        steps = self._create_steps_dict(task)
        steps.update({'steps-0-status': u"1"})
        steps.update({'steps-1-status': u"1"})
        steps.update({'steps-2-status': u"1"})
        steps.update({'steps-3-status': u"1"})
        steps.update({'steps-4-status': u"1"})
        response = self._update_task(task, steps)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.percent, 0)
        task = Task.objects.get(id=self.task1.id)
        for step in TaskStep.objects.filter(task=task):
            self.assertEqual(step.status, 0)

    def test_task_persent_set_to_zero_after_deleting_all_steps(self):
        task = Task.objects.get(id=self.task1.id)
        task.repeat = 2
        task.repeat_delta = 2
        task.from_repeating = 0
        task.save()
        steps = self._create_steps_dict(task)
        steps['steps-0-DELETE'] = "steps-0-DELETE"
        steps['steps-1-DELETE'] = "steps-1-DELETE"
        steps['steps-2-DELETE'] = "steps-2-DELETE"
        steps['steps-3-DELETE'] = "steps-3-DELETE"
        steps['steps-4-DELETE'] = "steps-4-DELETE"
        response = self._update_task(task, steps)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task1.id)
        self.assertEqual(task.percent, 0)




class CreateTaskWithTagsTestCase(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        TagFactory.create(name="Tag 1", author=self.john)
        TagFactory.create(name="Tag 2", author=self.john)
        TagFactory.create(name="Tag 3", author=self.john)

    def test_simply_create_task(self):
        task_name = "Task 1"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': 111,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': None,
                                                     u'ancestor': None, u"tags": [1,2,3]}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(task.owner.pk, self.john.pk)
        self.assertEqual(task.name, task_name)
        self.assertEqual(task.percent, 0)
        self.assertEqual(task.priority, "C")
        for tag in task.tags.all():
            tag.name in ["Tag 1", "Tag 2", "Tag 3"]
        self.assertEqual(task.tags.all().count(), 3)

    def test_simply_create_task_invalid_bad_tag_id(self):
        task_name = "Task 1"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({u'repeat': 0, u'description': None, u'finish_date': None,
                                                     u'percent': None, u'estimate_time': 111,
                                                     u'creation_date': None, u'type_finish_date': 0, u'owner': 1,
                                                     u'name': task_name, u'modification_date': None, u'author': 1,
                                                     u'status': 0, u'priority': None, u'task_project': 1, u'time': None,
                                                     u'ancestor': None, u"tags": [1, 2, 3, 99]}
                ), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EditTaskWithTagsTestCase(TestCase, UpdateTaskMixin):

    def setUp(self):
        self.john = UserFactory.create()
        self.enemy = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        self.tag1 = TagFactory.create(name="Tag 1", author=self.john)
        self.tag2 = TagFactory.create(name="Tag 2", author=self.john)
        self.tag3 = TagFactory.create(name="Tag 3", author=self.john)
        self.tag4 = TagFactory.create(name="Tag 4", author=self.john)
        self.list_1 = ListFactory.create(owner=self.john)
        self.task = TaskWithTagsAndStepsFactory(name="Task 1", owner=self.john, author=self.john, task_list=self.list_1,
                                                tags=[self.tag1, self.tag2, self.tag3])

    def _update_task(self, task, tags):
        url = reverse("task-detail", kwargs={"pk": task.id})
        response = self.client.put(url, json.dumps({"repeat": task.repeat, "description": task.description,
                                                    "percent": task.percent, "estimate_time": task.estimate_time,
                                                     "creation_date": task.creation_date.isoformat(),
                                                     "type_finish_date": task.type_finish_date,
                                                     "owner": task.owner.pk, "name": task.name,
                                                     "modification_date": task.modification_date.isoformat(),
                                                     "author": task.author.pk, "status": task.status,
                                                     "priority": task.priority, "task_project": task.task_list.pk,
                                                     "time": task.time, "ancestor": task.ancestor,
                                                     "from_repeating": task.from_repeating, "tags":tags,
                                                     "repeat_delta": task.repeat_delta, "is_active": True})
                , follow=True, content_type="application/json")
        return response

    def test_edit_task(self):
        task_name = "Task 1"
        response = self._update_task(self.task, [self.tag1.pk, self.tag3.pk])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task = Task.objects.get(id=self.task.id)
        self.assertEqual(task.owner.pk, self.john.pk)
        self.assertEqual(task.name, task_name)
        self.assertEqual(task.percent, 0)
        self.assertEqual(task.priority, "C")
        self.assertEqual(task.tags.all().count(), 2)
        for tag in task.tags.all():
            self.assertTrue(tag.name in ["Tag 1", "Tag 3"])


    def test_edit_task_invalid_bad_tag_id(self):
        task_name = "Task 1"
        url = reverse("task-list")
        response = self._update_task(self.task, [self.tag1.pk, self.tag3.pk, 999])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_task_invalid_tag_id_not_owner(self):
        """
           Tag nie należy do użytkownika
        """
        task_name = "Task 1"
        url = reverse("task-list")
        tag = TagFactory(name="Tag from enemy", author=self.enemy)
        response = self._update_task(self.task, [self.tag1.pk, self.tag3.pk, tag.id])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_task_tag_from_another_user_staying(self):
        """
            Tagi od innego użytkownika zostają, tylko są edytować tagi od Johna
        """
        tag_enemy1 = TagFactory(name="Tag from enemy 1", author=self.enemy)
        tag_enemy2 = TagFactory(name="Tag from enemy 2", author=self.enemy)
        task = TaskWithTagsAndStepsFactory(name="Task 1", owner=self.john, author=self.john,
                                           tags=[self.tag1, self.tag2, self.tag3,  tag_enemy1, tag_enemy2],
                                           task_list=self.list_1)
        response = self._update_task(task, [self.tag1.pk, self.tag3.pk])
        new_task = Task.objects.get(id=task.id)
        for tag in new_task.tags.all():
            self.assertTrue(tag.name in [self.tag1.name, self.tag3.name,
                                         tag_enemy1.name, tag_enemy2.name])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_task.tags.all().count(), 4)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result["tags"]), 2)
        for tag in result["tags"]:
            self.assertTrue(tag["name"] in [self.tag1.name, self.tag3.name])


class EditTasksWithLogStatisticsTestCase(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        self.task1 = TaskWithStepsFactory.create(task_list=List.objects.get(id=self.john.inbox_pk), owner=self.john,
                                    author=self.john, finish_date=None, estimate_time=3)
        self.task2 = TaskWithStepsFactory.create(task_list=List.objects.get(id=self.john.inbox_pk), owner=self.john,
                                    author=self.john, finish_date=None, estimate_time=5)
        self.task3 = TaskWithStepsFactory.create(task_list=List.objects.get(id=self.john.inbox_pk), owner=self.john,
                                    author=self.john, finish_date=None, estimate_time=7)

    def test_log_estimate_time_and_sum(self):
        self.task1.status = 1
        # we cannot change status and time in one request
        self.task1.save()

        self.task1.time = 11
        self.task1.save()

        self.task2.status = 1
        self.task2.save()

        self.task2.time = 13
        self.task2.save()

        statistics = TaskStatistics.objects.get(user=self.john, date=timezone.now())
        self.assertEqual(statistics.tasks_counter, 2)
        self.assertEqual(statistics.estimate_time_sum, 8)
        self.assertEqual(statistics.spend_time_sum, 24)

        #another entry to table TaskStatistics
        TaskStatistics.add_statistics(self.john, estimate_time=17, spend_time=19, date=date.today() + relativedelta(days=1))
        TaskStatistics.add_statistics(self.john, estimate_time=23, spend_time=29, date=date.today() + relativedelta(days=2))

        statistics_tomorrow = TaskStatistics.objects.get(user=self.john, date=date.today() + relativedelta(days=1))
        self.assertEqual(statistics_tomorrow.tasks_counter, 1)
        self.assertEqual(statistics_tomorrow.estimate_time_sum, 17)
        self.assertEqual(statistics_tomorrow.spend_time_sum, 19)

        statistics_day_after_tomorrow = TaskStatistics.objects.get(user=self.john, date=date.today() + relativedelta(days=2))
        self.assertEqual(statistics_day_after_tomorrow.tasks_counter, 1)
        self.assertEqual(statistics_day_after_tomorrow.estimate_time_sum, 23)
        self.assertEqual(statistics_day_after_tomorrow.spend_time_sum, 29)

    def test_log_estimate_time_and_sum_and_tasks_counter_repeating_task(self):
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.john, author=self.john, status=0, priority="A", estimate_time=49,
                                  task_list=List.objects.get(id=self.john.inbox_pk), repeat=1, finish_date=finish_date, from_repeating=1)
        task.status = 1
        task.save()
        task.time = 47
        task.estimate_time = 51
        task.save()
        statistics = TaskStatistics.objects.get(user=self.john, date=timezone.now())
        self.assertEqual(statistics.tasks_counter, 1)
        self.assertEqual(statistics.estimate_time_sum, 51)
        self.assertEqual(statistics.spend_time_sum, 47)

    def test_clean_spend_time_after_done_repeat_task(self):
        finish_date = date(2013, 10, 12)
        task = TaskFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                  task_list=List.objects.get(id=self.john.inbox_pk), repeat=1, finish_date=finish_date, from_repeating=1)
        task.time = 45
        task.status = 1
        task.save()
        new_task = Task.objects.get(id=task.id)
        self.assertEqual(new_task.time, 0)