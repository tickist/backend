#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
#from django.conf.urls.i18n import i18n_patterns as patterns
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns


# Format suffixes
# urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
