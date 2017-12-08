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
from dashboard.tasks.factory_classes import TaskFactory, TaskWithTagsAndStepsFactory, TagFactory

class TaskfromLists(TestCase):
    """
        Sprawdzenie czy lista tasków działa dobrze
        We have: 3 list, 12 tasks
    """
    def setUp(self):
        self.user = UserFactory.create()
        self.list_1 = ListFactory.create(owner=self.user)
        self.list_2 = ListFactory.create(owner=self.user, ancestor=self.list_1)
        self.list_3 = ListFactory.create(owner=self.user)
        #creating 12 tasks
        for mylist in [self.list_1, self.list_2, self.list_3]:
            for _ in range(2):
                TaskFactory.create(owner=self.user, author=self.user, task_list=mylist, status=0, priority="A")
            for _ in range(2):
                TaskFactory.create(owner=self.user, author=self.user, task_list=mylist, status=1, priority="C")
        #creating 2 tasks by user 2
        self.user2 = UserFactory.create()
        self.assertNotEqual(self.user.pk, self.user2.pk)
        self.list_user_2 = ListFactory.create(owner=self.user2)
        TaskFactory.create(owner=self.user2, author=self.user2, task_list=self.list_user_2, status=0)
        TaskFactory.create(owner=self.user2, author=self.user2, task_list=self.list_user_2, status=1)

        self.assertTrue(self.client.login(email=self.user.email, password="pass"))
        self.url = reverse("task-list")

    def _checking_tasks_list(self, response, tasks_from_database, status_code=status.HTTP_200_OK):
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(len(result), len(tasks_from_database))
        for i, task in enumerate(result):
            task_object = Task.objects.get(id=task['id'])
            self.assertEqual(task_object, tasks_from_database[i])

    def test_all_lists(self):
        #all tasks order by priority
        response = self.client.get(self.url, {"o": "priority"}, follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #all tasks order by - priority
        response = self.client.get(self.url, {"o": "-priority"}, follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user).order_by("-priority")
        self._checking_tasks_list(response, tasks_from_database)

        #only finished tasks ordered_by name
        response = self.client.get(self.url, {"o": "name", "status": "1"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, status=1).order_by("name")
        self._checking_tasks_list(response, tasks_from_database)

        #only unfinished tasks
        response = self.client.get(self.url, {"o": "-name", "status": "0"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, status=0).order_by("-name")
        self._checking_tasks_list(response, tasks_from_database)

    def test_selected_lists_without_permission(self):
        """ You dont have permission to get tasks from this list"""
        enemy = UserFactory.create()
        list_without_permission = ListFactory.create(owner=enemy)
        response = self.client.get(self.url, {"o": "priority", "list": list_without_permission.pk}, follow=True,
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_selected_lists(self):
        #tasks from list without descendant
        response = self.client.get(self.url, {"o": "priority", "list": self.list_3.pk}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, task_list=self.list_3).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #tasks from list with descendant
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user).filter(Q(task_list=self.list_2) |
                                                                          Q(task_list=self.list_1)).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #tasks from list with ancestor
        response = self.client.get(self.url, {"o": "priority", "list": self.list_2.pk}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, task_list=self.list_2).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #the same but only finished tasks
        #tasks from list without descendant
        response = self.client.get(self.url, {"o": "priority", "list": self.list_3.pk, "status": "1"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, task_list=self.list_3, status=1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #tasks from list with descendant
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk, "status": "1"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, status=1).filter(Q(task_list=self.list_2) |
                                                                                    Q(task_list=self.list_1)).\
            order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #tasks from list with ancestor
        response = self.client.get(self.url, {"o": "priority", "list": self.list_2.pk, "status": "1"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, task_list=self.list_2, status=1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #the same but only unfinished tasks
        #tasks from list without descendant
        response = self.client.get(self.url, {"o": "priority", "list": self.list_3.pk, "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, task_list=self.list_3, status=0).\
            order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #tasks from list with descendant
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk, "status": "0"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, status=0).\
            filter(Q(task_list=self.list_2) | Q(task_list=self.list_1)).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        #tasks from list with ancestor
        response = self.client.get(self.url, {"o": "priority", "list": self.list_2.pk, "status": "0"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user, task_list=self.list_2, status=0).\
            order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)


class TaskFromListTeamMateFiltersTest(TestCase):
    """
        Testing Filters for teammate
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
        for _ in range(4):
            TaskFactory.create(owner=self.user1, author=self.user1, task_list=self.list_1, status=1, priority="A")
        for _ in range(3):
            TaskFactory.create(owner=self.user2, author=self.user2, task_list=self.list_1, status=1, priority="A")
        for _ in range(2):
            TaskFactory.create(owner=self.user3, author=self.user3, task_list=self.list_1, status=1, priority="A")
        for _ in range(2):
            TaskFactory.create(owner=self.enemy, author=self.enemy, task_list=self.list_1, status=1, priority="A")

        self.assertTrue(self.client.login(email=self.user1.email, password="pass"))

    def _checking_tasks_list(self, response, tasks_from_database, status_code=status.HTTP_200_OK):
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(len(result), len(tasks_from_database))
        for i, task in enumerate(result):
            task_object = Task.objects.get(id=task['id'])
            self.assertEqual(task_object, tasks_from_database[i])

    def test_all_tasks(self):
        # from list
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk, "assign": "all"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner__pk__in=self.user1.all_team_mates_and_self(),
                                                  task_list=self.list_1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)
        # from all lists

        response = self.client.get(self.url, {"o": "priority", "assign": "all"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner__pk__in=self.user1.all_team_mates_and_self()).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

    def test_users_tasks(self):
        # from list
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk, "assign": self.user2.pk},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user2, task_list=self.list_1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        # from all lists
        response = self.client.get(self.url, {"o": "priority", "assign": self.user2.pk}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user2).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        # from list
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk, "assign": self.user3.pk},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user3, task_list=self.list_1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

        # from all lists
        response = self.client.get(self.url, {"o": "priority", "assign": self.user3.pk}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user3).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

    def test_my_tasks(self):
        # from list
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk, "assign": "me"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user1, task_list=self.list_1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)
        # from all lists

        response = self.client.get(self.url, {"o": "priority", "assign": "me"}, follow=True,
                                   content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user1).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)

    def test_user_not_from_my_team(self):
        response = self.client.get(self.url, {"o": "priority", "assign": str(self.enemy.pk)}, follow=True,
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_suspense_task(self):
        #create suspense tasks
        for _ in range(5):
            TaskFactory.create(owner=self.user1, author=self.user1, task_list=self.list_1, status=2, priority="A")
        response = self.client.get(self.url, {"o": "priority", "assign": str(self.user1.pk), "status": "2"},
                                   follow=True, content_type='application/json')
        tasks_from_database = Task.objects.filter(owner=self.user1, author=self.user1, status=2).order_by("priority")
        self._checking_tasks_list(response, tasks_from_database)


class SuspendTaskTest(TestCase):

    def setUp(self):
        self.url = reverse("task-list")
        self.user1 = UserFactory.create()
        self.yesterday = date.today() - timedelta(1)
        self.tomorrow = date.today() + timedelta(1)
        for _ in range(5):
            TaskFactory.create(owner=self.user1, author=self.user1, status=2, priority="A", suspend_date=self.yesterday)
        for _ in range(5):
            TaskFactory.create(owner=self.user1, author=self.user1, status=2, priority="A", suspend_date=self.tomorrow)
        #User need to permissions
        for my_list in List.objects.all():
            my_list.share_with.add(self.user1)
        self.assertTrue(self.client.login(email=self.user1.email, password="pass"))

    def test_unsuspense_task(self):
        response = self.client.get(self.url, {"o": "priority", "assign": str(self.user1.pk), "status": "2"},
                                   follow=True, content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 10)
        call_command("unsuspend_tasks")
        response = self.client.get(self.url, {"o": "priority", "assign": str(self.user1.pk), "status": "2"},
                                   follow=True, content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 5)
        response = self.client.get(self.url, {"o": "priority", "assign": str(self.user1.pk), "status": "0"},
                                   follow=True, content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 5)


class FilteredTaskByTags(TestCase):

    def setUp(self):
        self.url = reverse("task-list")
        self.john = UserFactory.create(username="john")

        self.enemy = UserFactory.create(username="Enemy")
        self.tag1 = TagFactory(name="Tag 1", author=self.john)
        self.tag2 = TagFactory(name="Tag 2", author=self.john)
        self.tag3 = TagFactory(name="Tag 3", author=self.john)
        self.tag_enemy = TagFactory(name="Tag enemy", author=self.enemy)
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_2 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_3 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_4 = ListFactoryShareWithUsers.create(owner=self.john)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        #Tagi 1 i 2
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag1,  self.tag3], task_list=self.list_1)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag1, self.tag3], task_list=self.list_1)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2], task_list=self.list_1)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3], task_list=self.list_1)
        #Tagi 1 i 3
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag1, self.tag3], task_list=self.list_2)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag1, self.tag3], task_list=self.list_2)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag1, self.tag3], task_list=self.list_2)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag1, self.tag3], task_list=self.list_2)
        #Tagi 2 i 3
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3], task_list=self.list_3)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3], task_list=self.list_3)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3], task_list=self.list_3)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3], task_list=self.list_3)
        #Tagi 2 i 3 i enemy
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3, self.tag_enemy], task_list=self.list_4)
        TaskWithTagsAndStepsFactory.create(owner=self.john, author=self.john, status=0, priority="A",
                                           tags=[self.tag2, self.tag3, self.tag_enemy], task_list=self.list_4)

        #Tags without tags
        for _ in range(2):
            TaskFactory.create(owner=self.john, author=self.john, task_list=self.list_3, status=1, priority="A")

    def test_filter_tasks_by_tag_one_list(self):
        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk,
                                              "tags": [self.tag1.pk, self.tag3.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 3)

        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk,
                                              "tags": [self.tag2.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 2)

        response = self.client.get(self.url, {"o": "priority", "list": self.list_1.pk,
                                              "tags": [self.tag1.pk, self.tag3.pk, self.tag2.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 4)

    def test_filter_tasks_by_tag_all_lists(self):
        response = self.client.get(self.url, {"o": "priority", "tags": [self.tag1.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 6)

        response = self.client.get(self.url, {"o": "priority", "tags": [self.tag1.pk, self.tag2.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 14)

        response = self.client.get(self.url, {"o": "priority", "tags": [self.tag2.pk, self.tag3.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 14)

        response = self.client.get(self.url, {"o": "priority", "tags": [self.tag3.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 13)

    def test_filter_tasks_by_enemy_tag(self):
        response = self.client.get(self.url, {"o": "priority", "tags": [self.tag3.pk, self.tag_enemy.pk]},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        result = json.loads(response.content.decode('utf-8'))

    def test_filter_tasks_tag_nothing(self):
        response = self.client.get(self.url, {"o": "priority", "tags": "null"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 2)


class DuedateAndEstimateTimeFilters(TestCase):

    def setUp(self):
        self.url = reverse("task-list")
        self.john = UserFactory.create(username="john")
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        for _ in range(4):
            TaskFactory.create(owner=self.john, author=self.john, status=2, priority="A", estimate_time=0,
                               task_list=self.john.inbox)
        for _ in range(6):
            TaskFactory.create(owner=self.john, author=self.john, status=2, priority="A", estimate_time=25,
                               finish_date=None, type_finish_date=0, task_list=self.john.inbox)
        TaskFactory.create(owner=self.john, author=self.john, status=2, priority="A", estimate_time=100,
                           finish_date=None, type_finish_date=0, task_list=self.john.inbox)
        TaskFactory.create(owner=self.john, author=self.john, status=2, priority="A", estimate_time=200,
                           finish_date=None, type_finish_date=0, task_list=self.john.inbox)
        TaskFactory.create(owner=self.john, author=self.john, status=2, priority="A", estimate_time=50,
                           finish_date=None, type_finish_date=0, task_list=self.john.inbox)
        TaskFactory.create(owner=self.john, author=self.john, status=2, priority="A", estimate_time=31,
                           finish_date=None, type_finish_date=0, task_list=self.john.inbox)

    def test_filter_without_estimate_time(self):
        response = self.client.get(self.url, {"o": "priority", "estimate_time": "0"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 14)

    def test_filter_estimate_time(self):
        response = self.client.get(self.url, {"o": "priority", "estimate_time__lt": "30"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 10)

        response = self.client.get(self.url, {"o": "priority", "estimate_time__gt": "30", "estimate_time__lt": "150"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 3)

        response = self.client.get(self.url, {"o": "priority", "estimate_time__gt": "30"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 4)

    def test_filter_without_due_date(self):
        response = self.client.get(self.url, {"o": "priority", "finish_date": "null"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 10)

    def test_list_undefined(self):
        """
         This test is connected with ticket #109
        """
        response = self.client.get(self.url, {"list": "undefined"},
                                   follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)