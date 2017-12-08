#-*- coding: utf-8 -*-

from django.test import LiveServerTestCase

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from users.models import User
from rest_framework import status
from users.factory_classes import UserFactory
from emails.models import Email
import json


class CheckEmailTest(TestCase):

    def setUp(self):
        self.john = UserFactory(username="john", email="john@example.com")
        self.client = Client(enforce_csrf_checks=False)

    def test_check_email_fail(self):
        response = self.client.post(reverse("registration-check_email"), json.dumps({"email": self.john.email}), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(reverse("registration-check_email"), json.dumps({"unknown": self.john.email}), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_email_ok(self):
        response = self.client.post(reverse("registration-check_email"), json.dumps({"email": "unknown@unkwnow.com"}), follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class SimpleRegistrationTest(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.username = "test"
        self.user_password = "pass"
        self.email = "test@example.com"


    def test_registration_pass(self):
        self.assertEqual(self.client.login(), False)
        self.assertEqual(User.objects.all().count(), 0)
        response = self.client.post(reverse("registration-registration"), json.dumps({'email': self.email,
                                                                                       "username": self.username,
                                                                                       "password": self.user_password}),
                                    follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.all().count(), 1)
        new_user = User.objects.get(id=1)
        self.assertEqual(new_user.username, self.username)
        self.assertEqual(new_user.email, self.email)
        self.assertEqual(new_user.is_confirm_email, False)
        self.assertEqual(new_user.is_active, True)
        self.assertTrue(new_user.check_password(self.user_password))
        #User is logged in. Redirect to /dashboard
        response = self.client.get('/', follow=True)
        email = Email.objects.get(user=new_user)
        registration_key_url = reverse("registration-confirm_email", args=[new_user.registration_key])
        self.assertGreaterEqual(email.body.find(registration_key_url), 0)
        response = self.client.get(registration_key_url)
        new_user = User.objects.get(id=1)
        self.assertEqual(new_user.is_confirm_email, True)

    def test_registration_failed(self):
        #bad email
        self.assertEqual(self.client.login(), False)
        self.assertEqual(User.objects.all().count(), 0)
        response = self.client.post(reverse("registration-registration"), json.dumps({'email': "test",
                                                                                       "username": self.username,
                                                                                       "password": "pass"}),
                                    follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #email is used
        john = UserFactory(username="john", email="john@example.com")
        response = self.client.post(reverse("registration-registration"), json.dumps({'email': john.email,
                                                                                       "username": self.username,
                                                                                       "password": "pass"}),
                                    follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #username and password are empty
        response = self.client.post(reverse("registration-registration"), json.dumps({'email': john.email,
                                                                                       "username": "",
                                                                                       "password": ""}),
                                    follow=True, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_email_resend(self):
        john = UserFactory(username="john", email="john@example.com", is_confirm_email=False)
        self.assertTrue(self.client.login(email=john.email, password="pass"))
        response = self.client.get(reverse("registration-send_email"), follow=True, content_type='application/json')
        registration_key_url = reverse("registration-confirm_email", args=[john.registration_key])
        email = Email.objects.get(user=john)
        self.assertGreaterEqual(email.body.find(registration_key_url), 0)