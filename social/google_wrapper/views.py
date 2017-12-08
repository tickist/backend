#-*- coding: utf-8 -*-

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _