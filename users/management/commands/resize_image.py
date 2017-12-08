#-*- coding: utf-8 -*-


from django.core.management.base import BaseCommand, CommandError
from users.utils import create_thumbnail
from users.models import User
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(is_active=True)
        for user in users:
            if user.avatar.name.find("default_avatar_user") == -1:
                create_thumbnail(user.avatar.name, user.id)
                print user.avatar.name
        self.stdout.write('Changing size of avatar change successfully \n')
