#-*- coding: utf-8 -*-
import json
from django.test import TestCase
from .models import LogError
from django.test.client import Client
from users.factory_classes import UserFactory
from rest_framework import status
from django.urls import reverse


class LogErrorTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.client = Client(enforce_csrf_checks=False)
        self.url = reverse("log-errors-add")
        self.message = "New message"
        self.stack = "new stack"
        self.user_id = self.user.id
        self.location = 'location'

    def test_create_new_log_error(self):

        self.assertEqual(LogError.objects.all().count(), 0)
        response = self.client.post(self.url, json.dumps({"message": self.message, 'stack': self.stack,
                                                     'location': self.location, 'user': self.user_id}), follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log_error = LogError.objects.get()
        self.assertEqual(log_error.message, self.message)
        self.assertEqual(log_error.stack, self.stack)
        self.assertEqual(log_error.user.id, self.user_id)
        self.assertEqual(log_error.location, self.location)
        self.assertTrue(log_error.hash)

    def test_trying_create_the_same_log_error(self):

        LogError(message=self.message, stack=self.stack, user=self.user, location=self.location).save()
        self.assertEqual(LogError.objects.all().count(), 1)
        response = self.client.post(self.url, json.dumps({"message": self.message, 'stack': self.stack,
                                                     'location': self.location, 'user': self.user_id}), follow=True,
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(LogError.objects.all().count(), 1)
