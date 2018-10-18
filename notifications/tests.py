#-*- coding: utf-8 -*-
import json
from datetime import date, timedelta
from django.utils import timezone
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.core.management import call_command
from rest_framework import status
from emails.models import Email
from notifications.models import DailySummary
from users.factory_classes import UserFactory
from dashboard.tasks.factory_classes import TaskFactory
from dashboard.lists.factory_classes import ListFactoryShareWithUsers
from dashboard.lists.tests.mixins import UpdateListMixin
from notifications.models import NotificationRecipient, NotificationContent
from notifications.tasks import send_notifications
from dashboard.tasks.tests.mixins import UpdateTaskMixin



class DailySummaryTestCase(TestCase):

    def setUp(self):
        # @TODO create static timezone object
        self.user = UserFactory.create(is_staff=True, daily_summary_hour=timezone.now() + timezone.timedelta(minutes=1))
        self.yesterday = timezone.now() - timedelta(days=1)
        self.today = timezone.now()
        for _ in range(5):
            TaskFactory.create(task_list=self.user.inbox, owner=self.user, author=self.user, status=0, priority="A",
                               finish_date=self.yesterday)
        for _ in range(5):
            TaskFactory.create(task_list=self.user.inbox, owner=self.user, author=self.user, status=0, priority="A",
                               finish_date=self.today)

    def test_send_daily_summary_to_users_only_ones_per_day(self):
        self.assertEqual(DailySummary.objects.all().count(), 0)
        call_command('send_daily_summary_to_users')
        self.assertEqual(DailySummary.objects.all().count(), 1)
        call_command('send_daily_summary_to_users')
        self.assertEqual(DailySummary.objects.all().count(), 1)
        call_command('send_daily_summary_to_users')
        self.assertEqual(DailySummary.objects.all().count(), 1)
        email = Email.objects.get(user=self.user)


class AssignsTaskToMeTestCase(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_1.share_with.add(self.bill)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def test_create_and_send_email_notification(self):
        task_name = "Task 1"
        url = reverse("task-list")
        response = self.client.post(url, json.dumps({"name": task_name, 'task_project': self.list_1.pk,
                                                     'owner': self.bill.pk}), follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notification_recipient = NotificationRecipient.objects.get(id=1)
        notification_content = NotificationContent.objects.get(id=1)
        self.assertEqual(notification_content.codename, "assigns_task_to_me")
        self.assertEqual(notification_recipient.user, self.bill)
        send_notifications()
        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.bill.pk).exists())
        self.assertTrue(Email.objects.filter(email=self.bill.email).exists())


class CompletesTaskFromSharedListTestCase(UpdateTaskMixin, TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_1.share_with.add(self.bill)
        self.list_1.share_with.add(self.kate)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        self.bill_task = TaskFactory.create(owner=self.bill, author=self.john, task_list=self.list_1)
        self.task = TaskFactory.create(owner=self.john, author=self.john, task_list=self.list_1)

    def test_create_email_notification_myself_task(self):
        self.task.status = 1
        self._update_task(self.task)
        notification_recipient = NotificationRecipient.objects.all()
        self.assertEqual(notification_recipient.count(), 2)
        notification_content = NotificationContent.objects.get()
        self.assertEqual(notification_content.codename, "completes_task_from_shared_list")
        send_notifications()
        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.bill.pk).exists())
        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.kate.pk).exists())
        self.assertTrue(Email.objects.filter(email=self.bill.email).exists())
        self.assertTrue(Email.objects.filter(email=self.kate.email).exists())

    def test_create_email_notification_bill_task(self):
        self.bill_task.status = 1
        self._update_task(self.bill_task)
        notification_recipient = NotificationRecipient.objects.all()
        self.assertEqual(notification_recipient.count(), 3)
        NotificationContent.objects.get(codename="completes_task_from_shared_list")
        send_notifications()

        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.bill.pk).exists())
        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.kate.pk).exists())
        self.assertTrue(Email.objects.filter(email=self.bill.email).exists())
        self.assertTrue(Email.objects.filter(email=self.kate.email).exists())




class ChangesTaskFromSharedListThatIsAssignedToMeTestCase(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def create_email_notification(self):
        pass


class RemovesMeFromSharedListTestCase(TestCase, UpdateListMixin):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_1.share_with.add(self.bill)
        self.list_1.share_with.add(self.kate)
        self.task = TaskFactory.create(task_list = self.list_1, owner=self.bill)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))

    def test_remove_user_from_shared_list_email(self):
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": [{'id':self.john.pk}, {'id':self.kate.pk}]})
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification_recipient = NotificationRecipient.objects.get(notification_content__codename="removes_me_from_shared_list")
        self.assertEqual(notification_recipient.user.email, self.bill.email)
        send_notifications()
        notification_recipient = NotificationRecipient.objects.get(id=notification_recipient.id)
        self.assertTrue(notification_recipient.is_read)
        self.assertTrue(Email.objects.filter(email=self.bill.email).exists())


class SharesListWithMe(UpdateListMixin, TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.bill)
        self.list_1.share_with.add(self.kate)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))

    def test_share_list_with_me_registered_user_email(self):
        """
            List is created we only update a list
        """
        put_dict = self._create_list_dictionary(self.list_1)
        put_dict.update({"share_with": [{'id':self.john.pk}, {'id':self.kate.pk}, {'id':self.bill.pk}]})
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.put(url, json.dumps(put_dict), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification_recipient = NotificationRecipient.objects.get(notification_content__codename="shares_list_with_me")
        self.assertEqual(notification_recipient.user.email, self.john.email)
        send_notifications()
        notification_recipient = NotificationRecipient.objects.get(id=notification_recipient.id)
        self.assertTrue(notification_recipient.is_read)
        self.assertTrue(Email.objects.filter(email=self.john.email).exists())

    def test_share_list_with_me_unregistered_user_email(self):
        pass


class ChangesTaskFromSharedListThatIsSssignedToMeTestCase(UpdateTaskMixin, TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_1.share_with.add(self.bill)
        self.list_1.share_with.add(self.kate)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        self.bill_task = TaskFactory.create(owner=self.bill, author=self.john, task_list=self.list_1)

    def test_change_task_assigned_to_bill(self):
        self.bill_task.priority = 'A'
        self.bill_task.repeat = 2
        self.bill_task.estimate_time = 30
        self._update_task(self.bill_task)
        notification_recipient = NotificationRecipient.objects.get(id=1)
        notification_content = NotificationContent.objects.get(id=1)
        self.assertEqual(notification_content.codename, "changes_task_from_shared_list_that_is_assigned_to_me")
        self.assertEqual(notification_recipient.user, self.bill)
        send_notifications()
        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.bill.pk).exists())
        self.assertTrue(Email.objects.filter(email=self.bill.email).exists())


class ChangesTaskFromSharedListThatIAssignedToHimHerTestCase(UpdateTaskMixin, TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_1.share_with.add(self.bill)
        self.list_1.share_with.add(self.kate)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))
        self.task = TaskFactory.create(owner=self.bill, author=self.john, task_list=self.list_1)

    def test_changes_a_task_from_a_shared_list_that_I_assigned_to_him_her(self):
        self.task.priority = 'A'
        self.task.repeat = 2
        self.task.estimate_time = 30
        self._update_task(self.task)
        notification_recipient = NotificationRecipient.objects.get(id=1)
        notification_content = NotificationContent.objects.get(id=1)
        self.assertEqual(notification_content.codename, "changes_task_from_shared_list_that_i_assigned_to_him_her")
        self.assertEqual(notification_recipient.user, self.john)
        send_notifications()
        self.assertTrue(NotificationRecipient.objects.filter(is_read=True, user__pk=self.john.pk).exists())
        self.assertTrue(Email.objects.filter(email=self.john.email).exists())

class LeavesSharedListTestCase(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.john)
        self.list_1.share_with.add(self.bill)
        self.list_1.share_with.add(self.kate)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))

    def test_leaves_shared_list_email(self):
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification_recipient = NotificationRecipient.objects.get(user=self.kate, notification_content__codename="leaves_shared_list")
        send_notifications()
        notification_recipient = NotificationRecipient.objects.get(id=notification_recipient.id)
        self.assertTrue(notification_recipient.is_read)
        self.assertTrue(Email.objects.filter(email=self.kate.email).exists())



class DeleteList(TestCase):

    def setUp(self):
        self.john = UserFactory.create()
        self.bill = UserFactory.create()
        self.kate = UserFactory.create()
        self.list_1 = ListFactoryShareWithUsers.create(owner=self.bill)
        self.list_1.share_with.add(self.john)
        self.list_1.share_with.add(self.kate)
        self.client = Client(enforce_csrf_checks=False)
        self.assertTrue(self.client.login(email=self.bill.email, password="pass"))

    def test_deletes_a_list_shared_with_me(self):
        url = reverse("list-detail", kwargs={'pk': self.list_1.pk})
        response = self.client.delete(url, {}, follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification_recipient1 = NotificationRecipient.objects.get(user=self.kate, notification_content__codename="deletes_list_shared_with_me")
        notification_recipient2 = NotificationRecipient.objects.get(user=self.john, notification_content__codename="deletes_list_shared_with_me")
        send_notifications()
        notification_recipient1 = NotificationRecipient.objects.get(id=notification_recipient1.id)
        notification_recipient2 = NotificationRecipient.objects.get(id=notification_recipient2.id)
        self.assertTrue(notification_recipient1.is_read)
        self.assertTrue(notification_recipient2.is_read)
        self.assertTrue(Email.objects.filter(email=self.kate.email).exists())