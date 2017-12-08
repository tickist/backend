# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from .views import LogError

urlpatterns = [
    url(_(r'^log_errors/add'), LogError.as_view(), name='log-errors-add'),
]

# Format suffixes
# urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
