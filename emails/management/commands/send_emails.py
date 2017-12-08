#-*- coding: utf-8 -*-


from django.core.management.base import BaseCommand, CommandError
from apps.mailing.emails.utils import send_non_send_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_non_send_email()

