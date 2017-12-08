#-*- coding: utf-8 -*-
from django.contrib import admin
from dashboard.lists.models import List, ShareListPending

admin.site.register(List)
admin.site.register(ShareListPending)