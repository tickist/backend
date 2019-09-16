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
            new_user2 = {
                'id': new_user.uid,
                'username': user.username,
                "email": user.email,
                "assignsTaskToMe": user.assigns_task_to_me,
                "dateJoined": user.date_joined.isoformat(),
                "inboxPk": user.inbox_pk,
                "orderTasksDashboard": user.order_tasks_dashboard,
                "changesTaskFromSharedListThatIsAssignedToMe": user.changes_task_from_shared_list_that_is_assigned_to_me,
                "changesTaskFromSharedListThatIAssignedToHimHer": user.changes_task_from_shared_list_that_i_assigned_to_him_her,
                "completesTaskFromSharedList": user.completes_task_from_shared_list,
                "dailySummaryHour": user.daily_summary_hour.isoformat(),
                "deletesListSharedWithMe": user.deletes_list_shared_with_me,
                "leavesSharedList": user.leaves_shared_list,
                "removesMeFromSharedList": user.removes_me_from_shared_list,
                "sharesListWithMe": user.shares_list_with_me,
                "avatarUrl": "",
                "dialogTimeWhenTaskFinishedInProject": user.dialog_time_when_task_finished_in_project,
                "allTasksView": user.all_tasks_view,
                "defaultTaskView": user.default_task_view,
                "defaultTaskViewTodayView": user.default_task_view_today_view,
                "defaultTaskViewOverdueView": user.default_task_view_overdue_view,
                "defaultTaskViewFutureView": user.default_task_view_future_view,
                "defaultTaskViewTagsView": user.default_task_view_tags_view,
                "overdueTasksSortBy": user.overdue_tasks_sort_by,
                "futureTasksSortBy": user.future_tasks_sort_by,
                "projectsFilterId": user.projects_filter_id,
                "tagsFilterId": user.tags_filter_id,
            }
            user_firebase.create(new_user2)

    def create_projects(self):
        col_projects = self.db.collection('projects')
        for project in List.objects.all().order_by('id'):
            project_firebase = col_projects.document()
            share_with = []
            share_with_ids = []
            for user in project.share_with.all():
                if hasattr(user, 'id'):
                    share_with.append({
                        "id":  self.global_ids['USER_{}'.format(user.id)],
                        "username": user.username,
                        "email": user.email,
                        "avatarUrl": ''
                    })
                    share_with_ids.append(self.global_ids['USER_{}'.format(user.id)])
                else:
                    share_with.append({
                        "username": user.username,
                        "email": user.email,
                        "status": user.is_active,

                    })

            new_project = {
                'id': project_firebase.id,
                'name': project.name,
                "isActive": project.is_active,
                "isInbox": project.is_inbox,
                "description": project.description,
                "ancestor": self.global_ids['PROJECT_{}'.format(project.ancestor_id)] if project.ancestor_id else None,
                "color": project.color,
                "shareWith": share_with,
                "owner": self.global_ids['USER_{}'.format(project.owner_id)],
                "defaultFinishDate": project.default_finish_date,
                "defaultPriority": project.default_priority,
                "defaultTypeFinishDate": project.default_type_finish_date,
                "dialogTimeWhenTaskFinished": project.dialog_time_when_task_finished,
                "taskView": project.task_view,
                "shareWithIds": share_with_ids,
            }
            project_firebase.create(new_project)
            print("New projekct {} is created".format(project.name))
            self.global_ids['PROJECT_{}'.format(project.id)] = project_firebase.id

    def create_tags(self):
        col_tags = self.db.collection('tags')
        for tag in Tag.objects.all().order_by('id'):
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

        for task in Task.objects.all().order_by('id'):
            task_firebase = col_tasks.document()
            # TODO skonczyc model
            isDone = task.status == 1
            onHold = task.status == 2

            taskProject = {
                'id': self.global_ids['PROJECT_{}'.format(task.task_list_pk)],
                'name': task.task_list.name,
                'color': task.task_list.color,
                'shareWithIds': [self.global_ids['USER_{}'.format(user.id)] for user in task.task_list.share_with.all()]
            }
            owner = {
                'id': self.global_ids['USER_{}'.format(task.owner.id)],
                'username': task.owner.username,
                'email': task.owner.email,
                'avatarUrl': ''
            }
            author = {
                'id': self.global_ids['USER_{}'.format(task.author.id)],
                'username': task.author.username,
                'email': task.author.email,
                'avatarUrl': ''
            }
            steps = []
            for step in task.steps.all():
                steps.append({
                    'id': step.id,
                    'name': step.name,
                    'status': step.status,
                    'order': step.order
                })

            tags = []
            tags_ids = []
            for tag in task.tags.all():
                tags.append({
                    "id": self.global_ids['TAG_{}'.format(tag.id)],
                    "name": tag.name,
                    "author": self.global_ids['USER_{}'.format(tag.author_id)],
                    "creationDate": tag.creation_date.strftime('%Y-%m-%dT%H:%M:%S.%f')
                })
                tags_ids.append(self.global_ids['TAG_{}'.format(tag.id)])

            new_task = {
                'id': task_firebase.id,
                'name': task.name,
                "description": task.description,
                "finishDate": task.finish_date.strftime('%Y-%m-%dT%H:%M:%S.%f') if task.finish_date else None,
                "finishTime": task.finish_time.strftime('%H:%M') if task.finish_time else None,
                "suspendDate": task.suspend_date.strftime('%Y-%m-%dT%H:%M:%S.%f') if task.suspend_date else None,
                "pinned": task.pinned,
                "isActive": task.is_active,
                "isDone": isDone,
                "onHold": onHold,
                "typeFinishDate": task.type_finish_date,
                "taskProject": taskProject,
                "owner": owner,
                "steps": steps,
                "priority": task.priority,
                "repeat": task.repeat,
                "repeatDelta": task.repeat_delta,
                "author": author,
                "fromRepeating": task.from_repeating,
                "tags": tags,
                "tagsIds": tags_ids,
                "time": task.time,
                "estimateTime": task.estimate_time
            }
            task_firebase.create(new_task)
            print("New task {} is created".format(task.name))
            self.global_ids['TASK_{}'.format(task.id)] = task_firebase.id
