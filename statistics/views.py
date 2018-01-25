# -*- coding: utf-8 -*-
from __future__ import division
import time
from datetime import date, timedelta, datetime
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from rest_framework import status
from dashboard.tasks.models import Task, TaskStatistics, Tag, PRIORITIES
from dashboard.lists.models import List
from django.db.models import Sum, Count
from django.db.models import Q, Avg, Max, Min, Sum
from commons.utils import zero_or_number, hex_code_colors


class DayStatistics(APIView):
    renderer_classes = [JSONRenderer]

    def __init__(self, **kwargs):
        super(DayStatistics, self).__init__(**kwargs)
        self.day = None
        self.day_format = None
        self.is_today = False

    def _get_priority_list(self, querylist):

        priorities = querylist.values_list("priority", flat=True).distinct().order_by("priority")
        priority_list = []
        for priority in priorities:
            priority_list.append({'name': u"%s" % priority,
                                  'time': querylist.filter(priority=priority).aggregate(Sum("estimate_time"))[
                                      'estimate_time__sum'],
                                  'count': querylist.filter(priority=priority).count(),
                                  'color': PRIORITIES[priority]['color']})
        return priority_list

    def _get_tags_list(self, querylist):

        tags = querylist.filter(tags__isnull=False).values_list("tags", flat=True).distinct()
        tags_list = []
        tasks_without_tags = querylist.filter(tags__isnull=True)
        tags_list.append({'name': u"Without tags",
                          'time': tasks_without_tags.aggregate(Sum("estimate_time"))['estimate_time__sum'],
                          'count': tasks_without_tags.count()})
        for tag in tags:
            tags_list.append({'name': u"Tag %s" % Tag.objects.get(id=tag).name,
                              'time': querylist.filter(tags=tag).aggregate(Sum("estimate_time"))['estimate_time__sum'],
                              'count': querylist.filter(tags=tag).count(),
                              'color': hex_code_colors()})
        return tags_list

    def _get_list(self, querylist):

        lists = querylist.values_list("task_list", flat=True).distinct()
        list_list = []
        for my_list in lists:
            listObject = List.objects.get(id=my_list)
            list_list.append({'name': listObject.name,
                              'time': querylist.filter(task_list=my_list).aggregate(Sum("estimate_time"))[
                                  'estimate_time__sum'],
                              'count': querylist.filter(task_list=my_list).count(),
                              'color': listObject.color})
        return list_list

    def _get_statistics_for_day_and_overdue_tasks(self):
        query_dict = {'is_active': 1, 'status': 0, 'owner__pk': self.request.user.pk}
        if self.is_today:
            query_dict['finish_date__lte'] = self.day
            queryset = Task.objects.filter(Q(**query_dict) | Q(pinned=True, status=0, owner__pk=self.request.user.pk))
        else:
            query_dict['finish_date'] = self.day
            queryset = Task.objects.filter(**query_dict)

        return {
            "date": {"value": "%s" % self.day_format},
            'estimate_time': {"value": queryset.aggregate(Sum("estimate_time"))['estimate_time__sum'] if
            queryset.aggregate(Sum("estimate_time"))['estimate_time__sum'] else 0},
            'tasks_count': {"value": queryset.count()},
            'priorities': self._get_priority_list(queryset),
            'tags': self._get_tags_list(queryset),
            'lists': self._get_list(queryset)
        }

    def get(self, request, *args, **kwargs):

        self.day = self.request.query_params.get("date",
                                                 datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        if not isinstance(self.day, date):
            self.day = datetime.strptime(self.day, '%Y-%m-%d')
        if self.day == datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            self.is_today = True
        self.day_format = self.day.strftime("%d-%m-%y")
        return Response(self._get_statistics_for_day_and_overdue_tasks(), status=status.HTTP_200_OK)


class GlobalStatistics(APIView):
    def get(self, request, *args, **kwargs):
        last_7th_days_tasks = sum_real_time = sum_estimation_time = 0
        day_start = date.today() - relativedelta(days=7)
        day_end = date.today()
        statistics = list(TaskStatistics.objects.filter(user__pk=self.request.user.pk, date__gte=day_start,
                                                        date__lte=day_end).order_by("date"))
        for stat in statistics:
            last_7th_days_tasks += stat.tasks_counter
            sum_estimation_time += stat.estimate_time_sum
            sum_real_time += stat.spend_time_sum
        current_estimation = (sum_estimation_time / sum_real_time) if zero_or_number(sum_real_time) else 0
        current_estimation = str(round(current_estimation, 2)) if current_estimation != 1 else "1"
        global_statistics = {
        'all_tasks': {'done': Task.objects.filter(is_active=1, owner__pk=request.user.pk, status=0).count(),
                      'undone': Task.objects.filter(is_active=1, owner__pk=request.user.pk, status=1).count(),
                      'suspend': Task.objects.filter(is_active=1, owner__pk=request.user.pk, status=2).count(),
                      'last_7th_days': last_7th_days_tasks,
                      'corrent_estimation': current_estimation,
                      'all': Task.objects.filter(is_active=1, owner__pk=request.user.pk).count()}}
        return Response(global_statistics, status=status.HTTP_200_OK)


class Charts(APIView):
    def get(self, request, *args, **kwargs):
        charts = {}
        today = timezone.now().replace(minute=0, hour=0, second=0, microsecond=0)
        self.day_start = self.request.query_params.get("date_start", today - timezone.timedelta(days=6))
        self.day_end = self.request.query_params.get("date_end", today)
        if not isinstance(self.day_start, date):
            self.day_start = timezone.datetime.strptime(self.day_start, '%d-%m-%y')
        if not isinstance(self.day_end, date):
            self.day_end = timezone.datetime.strptime(self.day_end, '%d-%m-%y')
        statistics = list(TaskStatistics.objects.filter(user__pk=self.request.user.pk, date__gte=self.day_start,
                                                        date__lte=self.day_end).order_by("date"))
        statistics_count = len(statistics)
        time_chart = []
        tasks_chart = []
        iterday = self.day_start
        i = 0
        while iterday <= self.day_end:
            timestamp = int(time.mktime(iterday.timetuple())) * 1000
            if statistics_count > i and statistics[i].date == iterday.date():
                tasks_chart.append({
                    'x': timestamp,
                    'tasks_counter': statistics[i].tasks_counter,
                })
                time_chart.append({
                    'x': timestamp,
                    'est_time': statistics[i].estimate_time_sum,
                    'spend_time': statistics[i].spend_time_sum,
                })
                i += 1
            else:
                tasks_chart.append({
                    'x': timestamp,
                    'tasks_counter': 0,
                })
                time_chart.append({
                    'x': timestamp,
                    'est_time': 0,
                    'spend_time': 0,
                })

            iterday = iterday + timezone.timedelta(days=1)
        charts['time_chart'] = time_chart
        charts['tasks_chart'] = tasks_chart
        charts['chart_min'] = int(time.mktime(self.day_start.timetuple())) * 1000
        charts['chart_max'] = int(time.mktime(self.day_end.timetuple())) * 1000

        return Response(charts, status=status.HTTP_200_OK)