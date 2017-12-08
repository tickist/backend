#-*- coding: utf-8 -*-
import json
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from users.models import User

notification_type = (("email", 'email'), ('web', 'web'))


class DailySummary(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()

    @classmethod
    def send_daily_summary(cls, user, date):
        if cls.objects.filter(user=user, datetime=date).exists():
            return False
        else:
            return True


class NotificationContent(models.Model):

    content = models.TextField(default="{}")
    codename = models.CharField(max_length=250)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')

    def __unicode__(self):
        return self.codename

    def get_template_content_json(self):
        return json.loads(self.content)

    def set_template_content_json(self, data):
        self.content = json.dumps(data)

    @property
    def extra_email_info(self):
        template_content = self.get_template_content_json()
        username = template_content['author_username']

        if self.codename == "removes_me_from_shared_list":
            list_name = template_content['list_name']
            template = "removes_me_from_shared_list.html"
            topic = "%s removed you from the shared list [list name]" % list_name
        elif self.codename == "shares_list_with_me":
            list_name = template_content['list_name']
            template = "shares_list_with_me.html"
            topic = "%s shared the to-do list [list name] with you on Tickist" % list_name
        elif self.codename == "assigns_task_to_me":
            template = "assigns_task_to_me.html"
            topic = "%s assigned a task to you" % username
        elif self.codename == "completes_task_from_shared_list":
            list_name = template_content['list_name']
            template = "completes_task_from_shared_list.html"
            topic = "%s completed a task from your shared list %s" % (username, list_name)
        elif self.codename == "changes_task_from_shared_list_that_is_assigned_to_me":
            template = "changes_task_from_shared_list_that_is_assigned_to_me.html"
            topic = "%s changed a task assigned to you" % (username)
        elif self.codename == "changes_task_from_shared_list_that_i_assigned_to_him_her":
            template = "changes_task_from_shared_list_that_i_assigned_to_him_her.html"
            topic = "%s changed a task that you'd assigned to him" % (username)
        elif self.codename == "leaves_shared_list":
            list_name = template_content['list_name']
            template = "leaves_shared_list.html"
            topic = "%s left the shared list %s" % (username, list_name)
        elif self.codename == "deletes_list_shared_with_me":
            list_name = template_content['list_name']
            template = "leaves_shared_list.html"
            topic = "%s left the shared list %s" % (username, list_name)

        return "notifications/emails/" + template, topic


class NotificationRecipient(models.Model):

    notification_content = models.ForeignKey(NotificationContent, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,  on_delete=models.CASCADE)
    email = models.EmailField()
    content_type = models.ForeignKey(ContentType,  on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    type = models.CharField(choices=notification_type, default="email", db_index=True, max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    is_read = models.BooleanField(default=False)