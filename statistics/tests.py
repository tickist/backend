#-*- coding: utf-8 -*-

from django.test import TestCase
from django.urls import reverse
from dashboard.tasks.factory_classes import TaskFactory, TagFactory, TaskWithTagsAndStepsFactory
from dashboard.lists.factory_classes import ListFactoryShareWithUsers
from users.factory_classes import UserFactory
from datetime import date, timedelta, datetime
from dashboard.tasks.models import TaskStatistics
from dateutil.relativedelta import relativedelta
import json


class DayStatisticsTest(TestCase):

    def setUp(self):
        self.james = UserFactory.create(username="James")
        self.assertTrue(self.client.login(email=self.james.email, password="pass"))
        self.tag1_name = "Tag 1"
        self.tag2_name = "Tag 2"
        self.tag3_name = "Tag 3"
        self.tag1 = TagFactory(name=self.tag1_name, author=self.james)
        self.tag2 = TagFactory(name=self.tag2_name, author=self.james)
        self.tag3 = TagFactory(name=self.tag3_name, author=self.james)
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.james)
        self.list_2 = ListFactoryShareWithUsers.create(owner=self.james)
        TaskWithTagsAndStepsFactory.create(priority='A', estimate_time=31, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[self.tag1,  self.tag3], task_list=self.list_1, type_finish_date=1)
        TaskWithTagsAndStepsFactory.create(priority='A', estimate_time=45, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[self.tag1,  self.tag3], task_list=self.list_1, type_finish_date=1)
        TaskWithTagsAndStepsFactory.create(priority='B', estimate_time=63, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[self.tag2], task_list=self.list_1, type_finish_date=1)
        TaskWithTagsAndStepsFactory.create(priority='B', estimate_time=92, finish_date=date.today(), owner=self.james,
                                author=self.james,tags=[self.tag2], task_list=self.list_1, type_finish_date=1)
        TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=54, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[], task_list=self.list_1, type_finish_date=1)
        TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=12, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[], task_list=self.list_1, type_finish_date=1)

        TaskWithTagsAndStepsFactory.create(priority='A', estimate_time=34, finish_date=date.today() + timedelta(4), owner=self.james,
                                author=self.james, tags=[self.tag1,  self.tag3], task_list=self.list_1, type_finish_date=0)
        TaskWithTagsAndStepsFactory.create(priority='A', estimate_time=42, finish_date=date.today() + timedelta(4), owner=self.james,
                                author=self.james, tags=[self.tag1,  self.tag3], task_list=self.list_1, type_finish_date=0)
        TaskWithTagsAndStepsFactory.create(priority='B', estimate_time=61, finish_date=date.today() + timedelta(4), owner=self.james,
                                author=self.james, tags=[self.tag2], task_list=self.list_1, type_finish_date=0)
        TaskWithTagsAndStepsFactory.create(priority='B', estimate_time=94, finish_date=date.today() + timedelta(4), owner=self.james,
                                author=self.james,tags=[self.tag2], task_list=self.list_2, type_finish_date=0)
        TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=52, finish_date=date.today() + timedelta(4), owner=self.james,
                                author=self.james, tags=[], task_list=self.list_2, type_finish_date=0)
        TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=11, finish_date=date.today() + timedelta(4), owner=self.james,
                                author=self.james, tags=[], task_list=self.list_2, type_finish_date=0)

        #tasks are done
        TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=12111, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[], task_list=self.list_1, status=1 )

        TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=12111, finish_date=date.today(), owner=self.james,
                                author=self.james, tags=[], task_list=self.list_1, status=1)

    def test_statistics_day(self):
        url = reverse("statistics-day")
        #url = reverse("statistics-day", kwargs={'date': "12-12-12"})
        response = self.client.get(url, follow=True, content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        tag1 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag1_name)][0]
        tag2 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag2_name)][0]
        tag3 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag3_name)][0]
        self.assertEqual(result['estimate_time']['value'], 31+45+63+92+54+12+10)
        self.assertEqual(result['tasks_count']['value'], 8)
        self.assertEqual(result['priorities'][0]['time'], 31+45) #priority A
        self.assertEqual(result['priorities'][0]['count'], 2)
        self.assertEqual(result['priorities'][1]['time'], 63+92) #priority B
        self.assertEqual(result['priorities'][1]['count'], 2)
        self.assertEqual(result['priorities'][2]['time'], 54+12+10) #priority C
        self.assertEqual(result['priorities'][2]['count'], 4)
        self.assertEqual(tag1['time'], 31+45)
        self.assertEqual(tag1['count'], 2)
        self.assertEqual(tag2['time'], 63+92)
        self.assertEqual(tag2['count'], 2)
        self.assertEqual(tag3['time'], 31+45)
        self.assertEqual(tag3['count'], 2)
        self.assertEqual(result['lists'][1]['time'], 31+45+63+92+54+12)
        self.assertEqual(result['lists'][1]['count'], 6)


    def test_statistics_day_user_choose_a_date(self):
        today_plus_4 = date.today() + timedelta(4)
        url = reverse("statistics-day")
        response = self.client.get(url, {'date': today_plus_4.strftime("%Y-%m-%d")},
                                   follow=True, content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        tag1 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag1_name)][0]
        tag2 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag2_name)][0]
        tag3 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag3_name)][0]
        self.assertEqual(result['estimate_time']['value'], 34+42+61+94+52+11)
        self.assertEqual(result['tasks_count']['value'], 6)
        self.assertEqual(result['priorities'][0]['time'], 34+42) #priority A
        self.assertEqual(result['priorities'][0]['count'], 2)
        self.assertEqual(result['priorities'][1]['time'], 61+94) #priority B
        self.assertEqual(result['priorities'][1]['count'], 2)
        self.assertEqual(result['priorities'][2]['time'], 52+11) #priority C
        self.assertEqual(result['priorities'][2]['count'], 2)
        self.assertEqual(tag1['time'], 31+45)
        self.assertEqual(tag1['count'], 2)
        self.assertEqual(tag2['time'], 63+92)
        self.assertEqual(tag2['count'], 2)
        self.assertEqual(tag3['time'], 31+45)
        self.assertEqual(tag3['count'], 2)
        self.assertEqual(result['lists'][1]['time'], 34+42+61+20)
        self.assertEqual(result['lists'][1]['count'], 3)

    def test_statistics_day_with_pinned_tasks(self):
        TaskWithTagsAndStepsFactory.create(priority='A', estimate_time=31, finish_date=date.today() + timedelta(4),
                                           owner=self.james, author=self.james, tags=[self.tag1,  self.tag3],
                                           task_list=self.list_1, type_finish_date=1, pinned=True)
        TaskWithTagsAndStepsFactory.create(priority='A', estimate_time=45, finish_date=date.today() + timedelta(4),
                                           owner=self.james,  author=self.james, tags=[self.tag1,  self.tag3],
                                           task_list=self.list_1, type_finish_date=1, pinned=True)
        url = reverse("statistics-day")
        #url = reverse("statistics-day", kwargs={'date': "12-12-12"})
        response = self.client.get(url, follow=True, content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        tag1 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag1_name)][0]
        tag2 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag2_name)][0]
        tag3 = [tag for tag in result['tags'] if tag['name'] == 'Tag {}'.format(self.tag3_name)][0]
        self.assertEqual(result['estimate_time']['value'], 31+45+63+92+54+12+45+31+10)
        self.assertEqual(result['tasks_count']['value'], 10)
        self.assertEqual(result['priorities'][0]['time'], 31+45+45+31) #priority A
        self.assertEqual(result['priorities'][0]['count'], 4)
        self.assertEqual(result['priorities'][1]['time'], 63+92) #priority B
        self.assertEqual(result['priorities'][1]['count'], 2)
        self.assertEqual(result['priorities'][2]['time'], 54+12+10) #priority C
        self.assertEqual(result['priorities'][2]['count'], 4)
        self.assertEqual(tag1['time'], 31+45+31+45)
        self.assertEqual(tag1['count'], 4)
        self.assertEqual(tag2['time'], 63+92)
        self.assertEqual(tag2['count'], 2)
        self.assertEqual(tag3['time'], 31+45+31+45)
        self.assertEqual(tag3['count'], 4)
        self.assertEqual(result['lists'][1]['time'], 31+45+63+92+54+12+31+45)
        self.assertEqual(result['lists'][1]['count'], 8)



class ChartTest(TestCase):

    def setUp(self):
        self.james = UserFactory.create(username="James")
        self.assertTrue(self.client.login(email=self.james.email, password="pass"))
        #Tasks statistics fill
        for arg in range(30):
            TaskStatistics.add_statistics(user=self.james, delta_tasks=2, estimate_time=5*arg, spend_time=7*arg,
                                      date=date.today() - relativedelta(days=30) + relativedelta(days=arg))

    def test_get_charts_data(self):
        url = reverse("charts")
        response = self.client.get(url, {"date_start": (date.today() - relativedelta(days=7)).strftime("%d-%m-%y"),
                                         "date_end":date.today().strftime("%d-%m-%y")}, follow=True,
                                   content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(result), 4)
        self.assertEqual(len(result['time_chart']), 8)
        self.assertEqual(len(result['tasks_chart']), 8)

    def test_get_charts_data_default_date(self):
        url = reverse("charts")
        response = self.client.get(url, follow=True,
                                   content_type='application/json')
        result = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(result), 4)
        self.assertEqual(len(result['time_chart']), 7)
        self.assertEqual(len(result['tasks_chart']), 7)

    def test_undone_task_and_chart(self):
        date_complete = datetime.now()-relativedelta(days=3)
        old_day_statistics = TaskStatistics.objects.get(date=date_complete, user=self.james)
        task = TaskWithTagsAndStepsFactory.create(priority='C', estimate_time=9, finish_date=date.today(),
                                                  owner=self.james, author=self.james, tags=[],
                                                  task_list=ListFactoryShareWithUsers.create(owner=self.james),
                                                  type_finish_date=0, when_complete=date_complete, status=1, time=9)
        task.status = 0
        task.save()
        new_day_statistics = TaskStatistics.objects.get(date=date_complete, user=self.james)
        self.assertEqual(old_day_statistics.spend_time_sum, new_day_statistics.spend_time_sum + 9)
        self.assertEqual(old_day_statistics.estimate_time_sum, new_day_statistics.estimate_time_sum + 9)
        self.assertEqual(old_day_statistics.tasks_counter, new_day_statistics.tasks_counter + 1)