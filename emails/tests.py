#-*- coding: utf-8 -*-
import datetime
import time
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from .utils import send_email, send_non_send_email
from .models import Email
from users.factory_classes import UserFactory


class EmailSendTestCase(TestCase):
    """
        Funkcja sprawdzająca czy można wysyłać maila
    """

    def setUp(self):
        self.user = UserFactory.create(email="user@example.com")


    def test_save_email_in_database_non_register_user(self):
        """
            Test sprawdzający czy można zapisać email do bazy danych
        """
        topic = u"Email_testowy"
        data_email = {}
        send_email(topic, template="emails/base_email.html", data_email={}, is_send_now=False,
                   email="test@example.com")

        email_db = Email.objects.get(id=1)
        self.assertEqual(Email.objects.count(), 1, msg=u"Liczba maili powinna być 1")
        self.assertEqual(email_db.is_send, False, msg=u"Wiadomość nie ma być wysłana")
        self.assertEqual(email_db.is_send_by_S3, False, msg=u"Nie wysyłamy maila przez Amazona")
        self.assertEqual(email_db.email, "test@example.com", msg=u"Sprawdzenie maila")
        self.assertEqual(email_db.topic, u"Email_testowy", msg=u"Sprawdzenie tematu")

        send_email(topic, template="emails/base_email.html", data_email={}, is_send_now=True,
                   email="test@example.com")

        email_db = Email.objects.get(id=2)
        self.assertEqual(Email.objects.count(), 2, msg=u"Liczba maili powinna być 1")
        self.assertEqual(email_db.is_send, True, msg=u"Wiadomość ma być wysłana")
        self.assertEqual(email_db.is_send_by_S3, False, msg=u"Nie wysyłamy maila przez Amazona")
        self.assertEqual(email_db.email, "test@example.com", msg=u"Sprawdzenie maila")
        self.assertEqual(email_db.topic, u"Email_testowy", msg=u"Sprawdzenie tematu")
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, topic)


    def test_save_email_in_database_register_user(self):
        """
            Test sprawdzający czy można zapisać email do bazy danych
        """
        topic = u"Email_testowy"
        data_email = {}

        send_email(topic, template="emails/base_email.html", user=self.user, data_email={},
                   is_send_now=False)

        email_db = Email.objects.get(id=1)
        self.assertEqual(Email.objects.count(), 1, msg=u"Liczba maili powinna być 1")
        self.assertEqual(email_db.is_send, False, msg=u"Wiadomość nie ma być wysłana")
        self.assertEqual(email_db.is_send_by_S3, False, msg=u"Nie wysyłamy maila przez Amazona")
        self.assertEqual(email_db.email, "user@example.com", msg=u"Sprawdzenie maila")
        self.assertEqual(email_db.topic, u"Email_testowy", msg=u"Sprawdzenie tematu")


class Send_EmailTestCase(TestCase):
    """
        Funkcja sprawdzająca  send_mail
    """

    def setUp(self):
        self.user = UserFactory.create(email="user@example.com")

    def test_send_at(self):
        topic = u"Email_testowy"
        send_email(topic, template="emails/base_email.html", data_email={},
                   is_send_now=False, send_at=datetime.datetime.now() + relativedelta(seconds=2),
                   email="test@example.com")

        self.assertEqual(Email.objects.filter(is_send=True).count(), 0, msg=u"Nic nie powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 1, msg=u"Musi być jeden niewysłany mail")
        time.sleep(2)
        send_non_send_email()
        self.assertEqual(Email.objects.filter(is_send=True).count(), 1, msg=u"Coś powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 0, msg=u"Nic nie powinno nie zostać wysłane")

    def test_is_send_now(self):
        topic = u"Email_testowy"
        send_email(topic, template="emails/base_email.html", data_email={},
                   is_send_now=False, email="test@example.com")
        self.assertEqual(Email.objects.filter(is_send=True).count(), 0, msg=u"Nic nie powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 1, msg=u"Musi być jeden niewysłany mail")

        send_email(topic, template="emails/base_email.html", data_email={},
                   is_send_now=True, email="test@example.com")

        self.assertEqual(Email.objects.filter(is_send=True).count(), 1, msg=u"Coś powinno zostać wysłane")
        self.assertEqual(Email.objects.filter(is_send=False).count(), 1, msg=u"Musi być jeden niewysłany mail")

    def test_show_by_key(self):
        topic = u"Email_testowy"
        data_email = {}

        send_email(topic, template="emails/base_email.html", user=self.user, data_email={},
                   is_send_now=False)

        email_db = Email.objects.all()[0]

        response = self.client.get(reverse('emails:show', args=[email_db.key]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('emails:show', args=[email_db.key + 'niematego']))
        self.assertEqual(response.status_code, 404)

    def test_key_unique(self):
        topic = u"Email_testowy"

        send_email(topic, template="emails/base_email.html", user=self.user, data_email={},
                   is_send_now=False)
        send_email(topic, template="emails/base_email.html", user=self.user, data_email={},
                   is_send_now=False)
        send_email(topic, template="emails/base_email.html", user=self.user, data_email={},
                   is_send_now=False)

        email = Email.objects.all().order_by('-id')[0]
        self.assertEqual(Email.objects.filter(key=email.key).count(), 1)
