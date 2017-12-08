#-*- coding: utf-8 -*-
from django.conf.urls import include, url
#from django.conf.urls.i18n import i18n_patterns as patterns
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from dashboard.tasks.views import TasksView, TaskDetail, TasksPostponeToToday

urlpatterns = [
       url(_(r'^tasks/$'), TasksView.as_view(), name='task-list'),
       url(_(r'^tasks/(?P<pk>\d+)/$'), TaskDetail.as_view(), name='task-detail'),
       url(_(r'^tasks/move_tasks_for_today/$'), TasksPostponeToToday.as_view(), name='task-postpone_all_tasks_to_today'),
]

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
