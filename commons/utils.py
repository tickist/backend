#-*- coding: utf-8 -*-
import string
import random
from random import choice
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.negotiation import BaseContentNegotiation
from emails.utils import send_email, async_send_email
from functools import wraps


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    def select_parser(self, request, parsers):
        """
        Select the first parser in the `.parser_classes` list.
        """
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix):
        """
        Select the first renderer in the `.renderer_classes` list.
        """
        return (renderers[0], renderers[0].media_type)


DEFAULT_TASK_VIEW = [('extended', 'extended'), ('simple', 'simple')]

def gen_passwd(length=40, chars=string.ascii_letters + string.digits):
    """ Get random password """
    return ''.join([choice(chars) for i in range(length)])


def polish_string(string, without_change_space=True):
    """
    Funkcja zamieniająca polskie litery na łacińskie i zamienia spacje na "_"
    @param string:
    @param without_change_space
    @return:
    """
    chars = [(u'ą',u'a'), (u'ę', u'e'), (u'ś', u's'), (u'ć', u'c'), (u'ż', u'z'), (u'ź', u'z'), (u'ó', u'o'),
            (u'ł', u'l'), (u'ń', u'n'), (u'Ą', u'A'), (u'Ę', u'E'), (u'Ś', u'S'), (u'Ć', u'C'), (u'Ż', u'Z'),
            (u'Ź', 'Z'), (u'Ó', u'O'), (u'Ł', u'L'), (u'Ń', u'N')]


    for charP, charL in chars:
        string = string.replace(charP, charL)
    if without_change_space:
        string = string.replace(" ", "-")
    return string


def is_number(arg):
    """
        Function checks if argument is a number or not
        @param arg
    """
    try:
        float(arg)
        return True
    except ValueError:
        return False


def zero_or_number(number):
    try:
        result = int(number)
    except (TypeError, ValueError):
        result = 0
    return result


def custom_proc(request):
    """
        Django custom proc
    """
    from django.conf import settings
    return {
        "DEBUG": settings.DEBUG,
        "PRODUCT": settings.PRODUCT,
        'FACEBOOK_FANPAGE': settings.FACEBOOK_FANPAGE,
        'GOOGLE_PLUS': settings.GOOGLE_PLUS,
        'TWITTER': settings.TWITTER
    }


def my_bool(string):

    if string == "false":
        return False
    elif string == "true":
        return True
    else:
        return bool(string)


def send_email_to_admins(topic="", template="", data={}):
    """
        Function sends email to all administrators
    """
    for admin in settings.ADMINS:
        async_send_email.apply_async(kwargs={"topic": topic, "template": template, "email": admin[1], "data_email": data})


def hex_code_colors():
    a = hex(random.randrange(0, 256))
    b = hex(random.randrange(0, 256))
    c = hex(random.randrange(0, 256))
    a = a[2:]
    b = b[2:]
    c = c[2:]
    if len(a) < 2:
        a = "0" + a
    if len(b) < 2:
        b = "0" + b
    if len(c) < 2:
        c = "0" + c
    z = a + b + c
    return "#" + z.upper()


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):

        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)
    return wrapper