#-*- coding: utf-8 -*-
from django.conf.urls import include, url
#from django.conf.urls.i18n import i18n_patterns as patterns
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from statistics.views import DayStatistics, GlobalStatistics, Charts

urlpatterns = [
       url(_(r'^day_statistics/$'), DayStatistics.as_view(), name='statistics-day'),
       url(_(r'^charts/$'), Charts.as_view(), name='charts'),
       url(_(r'^global/$'), GlobalStatistics.as_view(), name='statistics-global'),
]

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
