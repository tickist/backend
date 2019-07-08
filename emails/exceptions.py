#-*- coding: utf-8 -*-
from django.utils.translation import ugettext as _


class Diffrent_emails(Exception):

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class Email_is_empty(Exception):

    def __init__(self):
        self.parameter = _("Email field is empty")
    def __str__(self):
        return repr(self.parameter)
