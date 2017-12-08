#-*- coding: utf-8 -*-

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import ugettext as _