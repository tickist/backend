import os
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from users.models import User
from dashboard.tasks.models import Tag, TaskStatistics, Task
import simplejson as json

class Command(BaseCommand):
    src = 'db.json'
    dst = 'new_db.json'

    def handle(self, *args, **options):
        self.flush_database_tables()
        self.convert_database()

    def flush_database_tables(self):
        ContentType.objects.all().delete()
        Permission.objects.all().delete()
        Tag.objects.all().delete()
        Task.objects.all().delete()
        User.objects.all().delete()

    def convert_database(self):
        """
            Create testing database
        """

        old_database_json_file_handler = open(self.src, mode="r", encoding="utf-8")
        new_json_database_file_handler = open(self.dst, mode="w")
        tmp = old_database_json_file_handler.read().encode("UTF-8")
        old_database_json = json.loads(tmp)

        for arg in old_database_json:
            if arg["model"] == "contenttypes.contenttype":
                del arg['fields']['name']
            if arg["model"] == "users.user":
                arg['fields']['removes_me_from_shared_list'] = arg['fields']['removes_me_from_a_shared_list']
                del arg['fields']['removes_me_from_a_shared_list']

                arg['fields']['assigns_task_to_me'] = arg['fields']['assigns_a_task_to_me']
                del arg['fields']['assigns_a_task_to_me']

                arg['fields']['changes_task_from_shared_list_that_is_assigned_to_me'] = arg['fields']['changes_a_task_from_a_shared_list_that_is_assigned_to_me']
                del arg['fields']['changes_a_task_from_a_shared_list_that_is_assigned_to_me']

                arg['fields']['deletes_list_shared_with_me'] = arg['fields']['deletes_a_list_shared_with_me']
                del arg['fields']['deletes_a_list_shared_with_me']

                arg['fields']['shares_list_with_me'] = arg['fields']['shares_a_list_with_me']
                del arg['fields']['shares_a_list_with_me']

                arg['fields']['changes_task_from_shared_list_that_i_assigned_to_him_her'] = arg['fields']['changes_a_task_from_a_shared_list_that_I_assigned_to_him_her']
                del arg['fields']['changes_a_task_from_a_shared_list_that_I_assigned_to_him_her']

                arg['fields']['leaves_shared_list'] = arg['fields']['leaves_a_shared_list']
                del arg['fields']['leaves_a_shared_list']

                arg['fields']['completes_task_from_shared_list'] = arg['fields']['completes_a_task_from_a_shared_list']
                del arg['fields']['completes_a_task_from_a_shared_list']

                arg['fields']['avatar'] = "site_media/images/default_images/default_avatar_user.png"


        new_json_database_file_handler.write(json.dumps(old_database_json, encoding='utf-8'))
        call_command("loaddata", self.dst)

        user1 = User.objects.get(id=13)
        user1.set_password("passpass")
        user1.save()

        user2 = User.objects.get(id=6)
        user2.set_password("passpass")
        user2.save()

        user3 = User.objects.get(id=7)
        user3.set_password("passpass")
        user3.save()

        os.remove(self.dst)
