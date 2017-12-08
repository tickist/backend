from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from notifications.tasks import daily_summary


class Command(BaseCommand):

    def handle(self, *args, **options):
        daily_summary()