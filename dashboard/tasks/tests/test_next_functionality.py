#-*- coding: utf-8 -*-
import json
from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from django.db.models import Q
from rest_framework import status
from dashboard.tasks.models import Task
from dashboard.lists.models import List
from users.factory_classes import UserFactory
from dashboard.lists.factory_classes import ListFactory, ListFactoryShareWithUsers
from dashboard.tasks.factory_classes import TaskFactory

class TodayFunctionalityTest(TestCase):
    """
        Testowanie funkcjonalności znajdujacych się w zakładce TODAY
    """

    def setUp(self):
        self.url = reverse("task-list")
        yesterday = date.today() - timedelta(1)
        self.user = UserFactory.create()
        self.assertTrue(self.client.login(email=self.user.email, password="pass"))
        #Creating 3 tasks which are overdue
        for _ in range(3):
            TaskFactory.create(finish_date=yesterday, owner=self.user, author=self.user, status=0, priority="A")
        #Creating 3 tasks for today
        for _ in range(3):
            TaskFactory.create(finish_date=date.today(), owner=self.user, author=self.user, status=0, priority="A")
        #Creating 3 tasks for next week
        for i in range(3):
            TaskFactory.create(finish_date=date.today() + timedelta(i+1), owner=self.user, author=self.user,
                               status=0, priority="A")

        #User need to permissions
        for list in List.objects.all():
            list.share_with.add(self.user)

    def _checking_tasks_list(self, response, tasks_from_database, status_code=status.HTTP_200_OK):
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(len(result), len(tasks_from_database))
        for i, task in enumerate(result):
            task_object = Task.objects.get(id = task['id'])
            self.assertEqual(task_object, tasks_from_database[i])


    def test_today_tasks_list(self):
        response = self.client.get(self.url, {"finish_date": date.today(), "o": "type_finish_date", "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user,  status=0, finish_date=date.today()).\
            order_by("type_finish_date")
        self._checking_tasks_list(response, tasks_from_database)

    def test_overdue_tasks_list(self):
        response = self.client.get(self.url, {"finish_date__lt": date.today(), "o": "type_finish_date", "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user,  status=0, finish_date__lt=date.today()).\
            order_by("type_finish_date")
        self._checking_tasks_list(response, tasks_from_database)

    def test_nexttasks_list(self):
        response = self.client.get(self.url, {"finish_date__gt": date.today(), "o": "type_finish_date", "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user,  status=0, finish_date__gt=date.today()).\
            order_by("type_finish_date")
        self._checking_tasks_list(response, tasks_from_database)

    def test_functionality_you_can_do_this_too(self):
        """
            To do list should return all tasks which type_finish_date set to "to" and finish_date is greater then today
        """

        TaskFactory.create(finish_date=date.today() + timedelta(2), type_finish_date=0, owner=self.user,
                           author=self.user, status=0, priority="A")
        TaskFactory.create(finish_date=date.today() + timedelta(3), type_finish_date=0, owner=self.user,
                           author=self.user, status=0, priority="B")
        TaskFactory.create(finish_date=date.today() + timedelta(4), type_finish_date=0, owner=self.user,
                           author=self.user, status=0, priority="C")
        #User need to permissions
        for list in List.objects.all():
            list.share_with.add(self.user)

        response = self.client.get(self.url, {"finish_date__gt": date.today(), "type_finish_date": "0", "o":
            "type_finish_date", "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, type_finish_date=0,  status=0,
                                                  finish_date__gt=date.today()).order_by("type_finish_date")
        self._checking_tasks_list(response, tasks_from_database)

    def test_today_functionallity_with_pinned_tasks(self):
        TaskFactory.create(finish_date=date.today(), type_finish_date=0, owner=self.user,
                           author=self.user, status=0, priority="A", pinned=True)
        #User need to permissions
        for list in List.objects.all():
            list.share_with.add(self.user)

        response = self.client.get(self.url, {"finish_date": date.today(), "o": "type_finish_date", "status": "0", "pinned": True},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(Q(owner=self.user,  status=0, finish_date=date.today()) |
                                                  Q(pinned=True)).\
            order_by("type_finish_date")
        self._checking_tasks_list(response, tasks_from_database)

    def test_overdue_tasks_list_without_pinned_tasks(self):
        TaskFactory.create(finish_date=date.today(), type_finish_date=0, owner=self.user,
                           author=self.user, status=0, priority="A", pinned=False)
        #User need to permissions
        for list in List.objects.all():
            list.share_with.add(self.user)

        response = self.client.get(self.url, {"pinned": False, "finish_date__lt": date.today(), "o": "type_finish_date",
                                              "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(pinned=False, owner=self.user,  status=0, finish_date__lt=date.today()).\
            order_by("type_finish_date")
        self._checking_tasks_list(response, tasks_from_database)


class TasksPostponeToTodayTestCase(TestCase):

    def setUp(self):
        self.url = reverse("task-postpone_all_tasks_to_today")
        self.user = UserFactory.create()
        self.assertTrue(self.client.login(email=self.user.email, password="pass"))
        yesterday = date.today() - timedelta(1)
        #Creating 3 tasks which are overdue
        self.list_1 = ListFactory.create(owner=self.user)
        for _ in range(7):
            TaskFactory.create(finish_date=yesterday, owner=self.user, author=self.user, status=0, priority="A", task_list=self.list_1)
        #Creating 3 tasks for today
        for _ in range(3):
            TaskFactory.create(finish_date=date.today(), owner=self.user, author=self.user, status=0, priority="A", task_list=self.list_1)
        #Creating 3 tasks for next week
        for i in range(5):
            TaskFactory.create(finish_date=date.today() + timedelta(i+1), owner=self.user, author=self.user,
                               status=0, priority="A", task_list=self.list_1)

    def test_postpone_tasks(self):
        self.assertEqual(Task.objects.filter(owner=self.user, finish_date=date.today()).count(), 5)
        response = self.client.post(self.url, {}, follow=True, content_type='application/json' )
        self.assertEqual(Task.objects.filter(owner=self.user, finish_date=date.today()).count(), 12)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
