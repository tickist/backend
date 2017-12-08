#-*- coding: utf-8 -*-

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from commons.decorators import view_decorator

