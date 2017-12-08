#-*- coding: utf-8 -*-
from django.conf.urls import include, url
#from django.conf.urls.i18n import i18n_patterns as patterns
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from users.login.views import SimpleLoginView, SimpleLogoutView

urlpatterns = [
                       url(_(r'^login/$'), SimpleLoginView.as_view(), name='login-login'),
                       url(_(r'^logout/$'), SimpleLogoutView.as_view(), name='login-logout'),

                       ]

# Format suffixes
# urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
