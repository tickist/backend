from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from datetime import date, timedelta
from dashboard.tasks.models import Task
from datetime import date, timedelta
from dashboard.tasks.utils import unsuspend_tasks

class Command(BaseCommand):

    def handle(self, *args, **options):
        unsuspend_tasks()
