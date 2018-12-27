from django.core.management import call_command
from celery.task import task


@task
def db_backup():
    call_command('dbbackup')