from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from commons.gen_test_data.gen_database import Random_gen
from users.factory_classes import UserFactory
from dashboard.lists.factory_classes import ListFactory, ListFactoryShareWithUsers
from dashboard.lists.models import ShareListPending, List
from dashboard.tasks.factory_classes import TaskFactory, TaskWithStepsFactory, TaskWithTagsAndStepsFactory
from datetime import date, timedelta
from dashboard.tasks.models import Tag, TaskStatistics, Task
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from users.models import User

import firebase_admin
from firebase_admin import credentials, firestore, auth

tickist = credentials.Certificate("/srv/tickist/backend/credentials.json")
firebase_admin.initialize_app(tickist)


class Command(BaseCommand):
    global_ids = {}

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.db = firestore.client()

    def handle(self, *args, **options):

        self.remove_users()
        self.create_users()

        self.remove_tasks()
        self.remove_tags()
        self.remove_projects()

        self.create_projects()
        self.create_tags()
        self.create_tasks()


        print(self.global_ids)


    def remove_tasks(self):
        print("\nStart removing tasks")
        for k in self.db.collection('tasks').get():
            print("Task {} is removed".format(k.to_dict()['name']))
            k.reference.delete()

    def remove_tags(self):
        print("\nStart removing tags")
        for k in self.db.collection('tags').get():
            print("Tag {} is removed".format(k.to_dict()['name']))
            k.reference.delete()

    def remove_projects(self):
        print("\nStart removing projects")
        for k in self.db.collection('projects').get():
            print("Project {} is removed".format(k.to_dict()['name']))
            k.reference.delete()

    def remove_users(self):
        print("\nStart removing users auth")
        for user in auth.list_users().iterate_all():
            print("User {} is removed".format(user.uid))
            auth.delete_user(user.uid)

        print("\nStart removing users collection")
        for user in self.db.collection('users').get():
            print("User {} is removed".format(user.id))
            user.reference.delete()

    def create_users(self):
        print("\nStart creating users in Firebase")
        col_users = self.db.collection('users')
        for user in User.objects.all():
            new_user = auth.create_user(email=user.email, email_verified=True, password='passpass')
            self.global_ids['USER_{}'.format(user.id)] = new_user.uid
            print("New user {} is created".format(user.username))
            user_firebase = col_users.document(new_user.uid)
            # TODO skonczyc model
            new_user2 = {
                'id': new_user.uid,
                'username': user.username
            }
            user_firebase.create(new_user2)

    def create_projects(self):
        col_projects = self.db.collection('projects')
        for project in List.objects.all():
            project_firebase = col_projects.document()
            # TODO skonczyc model
            new_project = {
                'id': project_firebase.id,
                'name': project.name
            }
            project_firebase.create(new_project)
            print("New projekct {} is created".format(project.name))
            self.global_ids['PROJECT_{}'.format(project.id)] = project_firebase.id

    def create_tags(self):
        col_tags = self.db.collection('tags')
        for tag in Tag.objects.all():
            tag_firebase = col_tags.document()
            # TODO skonczyc model
            new_tag = {
                'id': tag_firebase.id,
                'name': tag.name,
                'author': self.global_ids['USER_{}'.format(tag.author_id)],
                'creationDate': tag.creation_date
            }
            tag_firebase.create(new_tag)
            print("New tag {} is created".format(tag.name))
            self.global_ids['TAG_{}'.format(tag.id)] = tag_firebase.id

    def create_tasks(self):
        col_tasks = self.db.collection('tasks')
        for task in Task.objects.all():
            task_firebase = col_tasks.document()
            # TODO skonczyc model
            new_task = {
                'id': task_firebase.id,
                'name': task.name
            }
            task_firebase.create(new_task)
            print("New task {} is created".format(task.name))
            self.global_ids['TASK_{}'.format(task.id)] = task_firebase.id
