# -*- coding: utf-8 -*-
from django import template
from django.template import Node
from django.template import defaulttags
from django import template
from django.utils.safestring import mark_safe
import random
import math

register = template.Library()


@register.filter("humanize_time")
def humanize_time(minutes, name=None):
    if minutes:
        hours = int(math.floor(minutes / 60))
        minutes = minutes % 60
        if hours > 0 and minutes > 0:
            humanize = str(hours) + "h " + str(minutes) + "m"
        elif hours > 0 and minutes == 0:
            humanize = str(hours) + "h"
        elif hours == 0 and minutes > 0:
            humanize = str(minutes) + "m"
        return humanize
    else:
        return "0m"
