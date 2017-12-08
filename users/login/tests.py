#-*- coding: utf-8 -*-

from django.test import LiveServerTestCase

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework import status
from users.factory_classes import UserFactory
import json


class SimpleLoginTest(TestCase):

    def setUp(self):
        self.john = UserFactory(username="john", email="john@example.com")
        self.client = Client(enforce_csrf_checks=False)

    def test_login(self):
        response = self.client.post(reverse("login-login"), json.dumps({'email': self.john.email,"password": "pass"}),
                                content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)


    def test_login_fail(self):
        #wrong password
        response = self.client.post(reverse("login-login"), json.dumps({'email': self.john.email,"password": "wrong"}),
                                content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        #email is bad
        response = self.client.post(reverse("login-login"), json.dumps({'email': "bad_email", "password": "wrong"}),
                                content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        # email is correct, user doesn't exist
        response = self.client.post(reverse("login-login"), json.dumps({'email': "bad_email@bad.pl", "password": "wrong"}),
                                content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fail_user_not_active(self):
        self.john.is_active = False
        self.john.save()
        response = self.client.post(reverse("login-login"), json.dumps({'email': self.john.email,"password": "wrong"}),
                                content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_is_not_confirm(self):
        import datetime
        self.john.date_joined = datetime.datetime(2000, 12, 12, 12, 12)
        self.john.is_confirm_email = False
        self.john.save()
        response = self.client.post(reverse("login-login"), json.dumps({'email': self.john.email,"password": "wrong"}),
                                content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        self.assertTrue(self.client.login(email=self.john.email, password="pass"))
        response = self.client.get(reverse("login-logout"), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)