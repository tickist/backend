# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.conf import settings
from django.utils import timezone
from commons.utils import zero_or_number
from dashboard.lists.models import List
from notifications.tasks import create_notification

choices_type_finish_date = [[0, _("by")], [1, _("on")]]
choices_repeat = [[0, __("no"), ""], [1, _("daily"), __("day(s)")], [2, __("daily (workweek)"), __("workday(s)")],
                  [3, __("weekly"), __("week(s)")], [4, __("monthly"), __("month(s)")],
                  [5, __("yearly"), __("year(s)")]]
choices_repeat_for_model = []
choices_type_finish_date_for_model = []
for arg in choices_repeat:
    choices_repeat_for_model.append(arg[0:2])

PRIORITIES = {'A': {
    'name': 'A',
    'color': '#cc324b'
}, 'B': {
    'name': 'B',
    'color': '#FF99B2'
}, 'C': {
    'name': 'C',
    'color': '#ffffff'
}}

choices_priority = [('A', "A"), ("B", "B"), ("C", "C")]
choices_from_repeating = [[0, _("completion date")], [1, _("due date")]]
choices_status = [[0, _("is undone")], [1, _("is done")], [2, _("is suspended")]]


class Tag(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    modification_date = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        unique_together = ('name', 'author',)

    def tasks_counter(self):
        return Task.objects.filter(tags=self, status=0, is_active=True).count()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class TaskStatistics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE)
    estimate_time_sum = models.IntegerField(default=0)
    spend_time_sum = models.IntegerField(default=0)
    date = models.DateField(db_index=True)
    tasks_counter = models.IntegerField(default=0)

    @classmethod
    def add_statistics(cls, user, delta_tasks=1, estimate_time=0, spend_time=0, date=None):
        """
            Add new task statistics
        """
        if date is None:
            date = timezone.now()
        statistics, created = cls.objects.get_or_create(date=date, user=user)
        statistics.estimate_time_sum = F('estimate_time_sum') + zero_or_number(estimate_time)
        statistics.spend_time_sum = F('spend_time_sum') + zero_or_number(spend_time)
        statistics.tasks_counter = F('tasks_counter') + delta_tasks
        statistics.save()


class Task(models.Model):
    """
    Model for tasks
    """
    name = models.CharField(max_length=500)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.DO_NOTHING)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="author", on_delete=models.DO_NOTHING)
    priority = models.CharField(choices=choices_priority, default="C", db_index=True, max_length=1)
    description = models.TextField(null=True, blank=True)
    task_list = models.ForeignKey(List, null=True, blank=True, on_delete=models.DO_NOTHING)
    estimate_time = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    ancestor = models.ForeignKey('self', related_name='self', null=True, blank=True, on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    modification_date = models.DateTimeField(editable=False, auto_now=True)
    finish_date = models.DateField(null=True, blank=True)
    finish_time = models.TimeField(null=True, blank=True)
    type_finish_date = models.IntegerField(choices=choices_type_finish_date, null=True, blank=True)
    percent = models.IntegerField(default=0)
    repeat = models.IntegerField(choices=choices_repeat_for_model, default=0)
    repeat_delta = models.IntegerField(default=1)
    from_repeating = models.IntegerField(choices=choices_from_repeating, default=0)
    status = models.IntegerField(default=0, choices=choices_status)
    when_complete = models.DateTimeField(editable=False, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    suspend_date = models.DateField(null=True, blank=True)  # task is suspended to date
    tags = models.ManyToManyField(Tag, blank=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @classmethod
    def create_notification(cls, old_task, new_task, request, form=None):
        content = {}
        recipients = []
        if old_task:
            if old_task.status == 0 and new_task.status == 1:
                content['author_username'] = request.user.username
                content['author_email'] = request.user.email
                content['list_name'] = new_task.task_list.name
                for user in new_task.task_list.share_with.all():
                    if request.user.id != user.id:
                        recipients.append(user)
                create_notification("completes_task_from_shared_list", new_task, content, recipients=recipients)

            if len(form.changed_data) > 0:
                content['changes'] = []
                content['author_username'] = request.user.username
                content['author_email'] = request.user.email
                for arg in form.changed_data:
                    if arg in ['repeat', 'repeat_delta']:
                        pass
                    # Tags is releted to only one user
                    if arg in ['tags']:
                        continue

                    content['changes'].append(u"{arg} has changed from {old} to {new}".format(arg=arg.capitalize(),
                                                                                              old=str(getattr(old_task,
                                                                                                              arg)),
                                                                                              new=str(getattr(new_task,
                                                                                                              arg))))
                if request.user == new_task.author and new_task.author != new_task.owner:
                    codename = "changes_task_from_shared_list_that_is_assigned_to_me"
                    create_notification(codename, new_task, content, recipients=[new_task.owner])
                elif request.user == new_task.owner and new_task.author != new_task.owner:
                    content['is_author'] = True
                    codename = "changes_task_from_shared_list_that_i_assigned_to_him_her"
                    create_notification(codename, new_task, content, recipients=[new_task.author])
                elif new_task.author != new_task.owner != request.user:
                    codename = "changes_task_from_shared_list_that_i_assigned_to_him_her"

                    content['is_author'] = False
                    create_notification(codename, new_task, content, recipients=[new_task.author, new_task.owner])
        else:
            codename = "assigns_task_to_me"
            content['author_username'] = new_task.author.username
            content['email_author'] = new_task.author.email
            if new_task.author != new_task.owner:
                recipients.append(new_task.owner)

            create_notification(codename, new_task, content, recipients=recipients)

    @property
    def task_list_pk(self):
        return self.task_list_id

    @property
    def owner_pk(self):
        return self.owner_id

    def repeat_humanize(self):
        if self.repeat > 0:
            return "every %s %s" % (self.repeat_delta, choices_repeat[self.repeat][2])
        else:
            return ""

    @property
    def priority_color(self):
        if self.priority == "A":
            color = "#cc324b;"
        elif self.priority == "B":
            color = "#FF99B2;"
        elif self.priority == "C":
            color = "#fff;"
        else:
            color = "#fff;"

        return color

    def due_date_or_complation(self, delta, workweek=False):
        old_finish_date = self.finish_date if self.finish_date else datetime.date.today()
        if self.from_repeating == 0:
            self.finish_date = datetime.date.today() + delta
        elif self.from_repeating == 1:
            self.finish_date = self.finish_date + delta

        if workweek:
            single_day = datetime.timedelta(days=1)
            day_off_count = 0
            day = old_finish_date
            while day != self.finish_date:
                if day.weekday() in [5, 6]:
                    day_off_count += 1
                day += single_day
            self.finish_date = self.finish_date + relativedelta(days=day_off_count)
            if self.finish_date.weekday() == 5:
                # It is saturday move to Monday
                self.finish_date = self.finish_date + relativedelta(days=2)
            elif self.finish_date.weekday() == 6:
                # it is sunday move to Monday
                self.finish_date = self.finish_date + relativedelta(days=1)

    def repeting_task(self):
        if self.repeat == 1:
            self.due_date_or_complation(relativedelta(days=self.repeat_delta))
        elif self.repeat == 2:
            self.due_date_or_complation(relativedelta(days=self.repeat_delta), workweek=True)
        elif self.repeat == 3:
            self.due_date_or_complation(relativedelta(weeks=self.repeat_delta))
        elif self.repeat == 4:
            self.due_date_or_complation(relativedelta(months=self.repeat_delta))
        elif self.repeat == 5:
            self.due_date_or_complation(relativedelta(years=self.repeat_delta))
        self.status = 0
        self.percent = 0
        self.pinned = False
        TaskStep.objects.filter(task=self).update(status=0)
        self.time = 0

    @property
    def finish_date_dateformat(self):
        iso = None
        if self.finish_date:
            iso = int(self.finish_date.strftime("%s")) * 1000
        return self.finish_date

    def save(self, *args, **kwargs):
        """
            Saving model in database, and make some additional things (e.g. repeating tasks)
        """
        old_task = None
        if self.id:
            # if we create the task than self.id is None
            # import ipdb;ipdb.set_trace()
            old_task = Task.objects.get(id=self.id)
            is_status_change = old_task.status != self.status
            is_estimate_time_change = old_task.estimate_time != self.estimate_time
            is_time_change = old_task.time != self.time
            # print "#####"
            # print "is status change %s" % is_status_change
            # print "is_estimata_time_change %s" % is_estimate_time_change
            # print "is_time_change %s" % is_time_change
            # print "time %s" % self.time
            # print "old time %s" % old_task.time
            # print "$$$$$$"
            # import ipdb;ipdb.set_trace()
            if is_status_change and not is_estimate_time_change and not is_time_change:

                if old_task.status == 0 and self.status == 1:
                    TaskStatistics.add_statistics(user=self.owner, delta_tasks=1,
                                                  estimate_time=zero_or_number(self.estimate_time),
                                                  spend_time=zero_or_number(self.time))
                    if self.repeat > 0:
                        self.repeting_task()
                    self.when_complete = timezone.now()
                if old_task.status == 1 and self.status == 0:
                    TaskStatistics.add_statistics(user=self.owner, delta_tasks=-1,
                                                  estimate_time=zero_or_number(self.estimate_time) * (-1),
                                                  spend_time=zero_or_number(self.time) * (-1),
                                                  date=self.when_complete.date())
                    self.when_complete = None

            if is_estimate_time_change and not is_time_change and self.when_complete and not is_status_change:
                TaskStatistics.add_statistics(user=self.owner, delta_tasks=0,
                                              estimate_time=zero_or_number(self.estimate_time - old_task.estimate_time),
                                              spend_time=0, date=self.when_complete)

            if is_time_change and not is_estimate_time_change and self.when_complete and not is_status_change:
                TaskStatistics.add_statistics(user=self.owner, delta_tasks=0, estimate_time=0,
                                              spend_time=zero_or_number(self.time - old_task.time),
                                              date=self.when_complete)

            if is_estimate_time_change and is_time_change and self.when_complete and not is_status_change:
                TaskStatistics.add_statistics(user=self.owner, delta_tasks=0,
                                              estimate_time=zero_or_number(self.estimate_time - old_task.estimate_time),
                                              spend_time=zero_or_number(self.time - old_task.time),
                                              date=self.when_complete)
            # Zadanie z ustawionym powtarzaniem nie powinien miec real time bo to zadanie jest nieskończone
            if self.repeat > 0:
                self.time = 0
                self.status = 0
        if not self.owner:
            self.owner = self.author
        super(Task, self).save(*args, **kwargs)


class TaskStep(models.Model):
    name = models.CharField(max_length=200)
    task = models.ForeignKey(Task, related_name="steps", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="step_author", blank=True, null=True,
                               on_delete=models.DO_NOTHING)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_last_change", blank=True, null=True,
                              on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    modification_date = models.DateTimeField(editable=False, auto_now=True)
    status = models.IntegerField(default=0, choices=[[0, _("is undone")], [1, _("is done")]])
    order = models.PositiveIntegerField(default=100)  # 100 this is random value (it is not important)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return self.name
