#-*- coding: utf-8 -*-
import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Q, Avg, Max, Min, Sum
from django.utils.translation import ugettext_lazy as _
from emails.utils import async_send_email, send_email
from users.models import User
from .models import DailySummary, NotificationContent, NotificationRecipient
from celery.task import task


@task
def daily_summary():
    from dashboard.tasks.models import Task
    users = User.objects.filter(is_active=True,  daily_summary_hour__gt=timezone.now(),
                                daily_summary_hour__lt=timezone.now() + timezone.timedelta(minutes=30), is_staff=True)
    for user in users:
        now = timezone.now()
        user_date = datetime.datetime(now.year, now.month, now.day, user.daily_summary_hour.hour,
                                      user.daily_summary_hour.minute)
        if DailySummary.send_daily_summary(user, user_date):
            today = timezone.now()
            today_tasks = Task.objects.filter(owner=user, is_active=True, status=0, finish_date=today, pinned=False).order_by("priority")
            overdue_tasks = Task.objects.filter(owner=user, is_active=True, status=0, finish_date__lt=today, pinned=False).order_by("priority")
            pinned_tasks = Task.objects.filter(owner=user, is_active=True, status=0, pinned=True).order_by("priority")
            tasks_for_statistics = Task.objects.filter(Q(owner=user, is_active=True, status=0, finish_date__lte=today) |
                                                       Q(pinned=True, status=0, owner=user))

            if tasks_for_statistics.count() > 0:
                statistics = {'all_tasks_counter': tasks_for_statistics.count(),
                              'all_tasks_estimate_time': tasks_for_statistics.aggregate(Sum("estimate_time"))['estimate_time__sum'],
                              'priority_A_tasks_counter': tasks_for_statistics.filter(priority="A").count(),
                              'priority_A_estimate_time': tasks_for_statistics.filter(priority="A").aggregate(Sum("estimate_time"))['estimate_time__sum'],
                              'priority_B_tasks_counter': tasks_for_statistics.filter(priority="B").count(),
                              'priority_B_estimate_time': tasks_for_statistics.filter(priority="B").aggregate(Sum("estimate_time"))['estimate_time__sum'],
                              'priority_C_tasks_counter': tasks_for_statistics.filter(priority="C").count(),
                              'priority_C_estimate_time': tasks_for_statistics.filter(priority="C").aggregate(Sum("estimate_time"))['estimate_time__sum'],

                }

                async_send_email(topic=_("Tickist: Your tasks for today (%s-%s-%s)" % (str(today.day).zfill(2), str(today.month).zfill(2), today.year)),
                                 template="notifications/emails/daily.html", email=user.email, user=user,
                                 data_email={'today_tasks': today_tasks, "overdue_tasks": overdue_tasks,  "user": user,
                                             "pinned_tasks": pinned_tasks, "statistics": statistics})

                DailySummary(user=user, datetime=user_date).save()


def create_notification(codename, instance, content, types=None, recipients=None):

    if not types:
        types = ['email']
    if not recipients:
        recipients = []
    notification_content = NotificationContent()
    notification_content.set_template_content_json(content)
    notification_content.codename = codename
    notification_content.save()

    for user in recipients:
        if user.is_notification_codename_send(codename):
            notification_recipient = NotificationRecipient()
            for type in types:
                notification_recipient.type = type
            notification_recipient.user = user
            notification_recipient.notification_content = notification_content
            notification_recipient.object_id = instance.id
            notification_recipient.content_type = ContentType.objects.get_for_model(instance)
            notification_recipient.save()





@task
def send_notifications():
    #email sends
    notifications = NotificationRecipient.objects.select_related("notification_content").\
        filter(is_read=False, type="email")
    for notification in notifications:
        template, topic = notification.notification_content.extra_email_info
        data_email = notification.notification_content.get_template_content_json()
        data_email['username'] = notification.user.username
        if notification.content_type.name == "task":
            data_email['task'] = notification.content_object
        elif notification.content_type.name == "list":
            data_email['list'] = notification.content_object
        async_send_email(topic=topic, template=template, email=notification.email, user=notification.user,
                             data_email=data_email)
        notification.is_read = True
        notification.save()
