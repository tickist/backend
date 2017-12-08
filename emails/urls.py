# -*- coding: utf-8 -*-

#from django.conf.urls.defaults import *
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from .views import show_email

app_name = "email"

urlpatterns = [
    url(_(r'^show/(?P<key>[\w\-_]+)$'), show_email, name='show')
]
