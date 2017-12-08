from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from commons.gen_test_data.gen_database import Random_gen
from users.factory_classes import UserFactory
from dashboard.lists.factory_classes import ListFactory, ListFactoryShareWithUsers
from dashboard.lists.models import ShareListPending
from dashboard.tasks.factory_classes import TaskFactory, TaskWithStepsFactory, TaskWithTagsAndStepsFactory
from datetime import date, timedelta
from dashboard.tasks.models import Tag, TaskStatistics
from dateutil.relativedelta import relativedelta
from django.utils import timezone


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.testing_database()

    def testing_database(self):
        """
            Create testing database
        """
        call_command("migrate", interactive=False)
        #create Random Class instance
        random = Random_gen()

        #create users
        self.stdout.write("Starting create users")
        bill = UserFactory.create(username="bill", is_superuser=True, is_staff=True)
        james = UserFactory.create(username="james")
        kate = UserFactory.create(username="kate")

        greg = UserFactory.create()

        #create tags list

        bill_tags = Tag.objects.filter(author=bill)
        kate_tags = Tag.objects.filter(author=kate)
        james_tags = Tag.objects.filter(author=james)

        #create lists
        self.stdout.write("Starting create lists")
        list1 = ListFactoryShareWithUsers.create(name="Project 1", owner=bill, share_with=[bill, james, kate])
        list2 = ListFactoryShareWithUsers.create(name="Project 2", owner=bill, share_with=[bill, james, kate],
                                                 ancestor=list1, description=random.text_gen(len_max=200))
        list3 = ListFactoryShareWithUsers.create(name="Project 3", owner=james, share_with=[bill, james, kate],
                                                 ancestor=list2, description=random.text_gen(len_max=200))
        list4 = ListFactoryShareWithUsers.create(name="Project 4", owner=james, share_with=[bill, james, kate])
        list5 = ListFactoryShareWithUsers.create(name="Project 5", owner=kate, share_with=[bill, james, kate],
                                                 ancestor=list4)
        list6 = ListFactoryShareWithUsers.create(name="Project 6", owner=kate, share_with=[bill, james, kate],
                                                 ancestor=list4, description=random.text_gen(len_max=200))
        ListFactoryShareWithUsers.create(name="List 7", owner=greg, share_with=[greg])

        #create sharewith pending
        ShareListPending(email="new_user1@example.com", user=bill, list=list1).save()
        ShareListPending(email="new_user2@example.com", user=bill, list=list1).save()
        ShareListPending(email="new_user3@example.com", user=bill, list=list1).save()

        ShareListPending(email="new_user1@example.com", user=bill, list=list4).save()
        ShareListPending(email="new_user2@example.com", user=bill, list=list4).save()
        ShareListPending(email="new_user3@example.com", user=bill, list=list4).save()


        #create undone tasks with steps
        self.stdout.write("Starting create undone tasks with steps")
        TaskWithStepsFactory.create(name='Task 1 on Project 1', task_list=list1, owner=bill, author=bill, finish_date=date.today(),
                                    description=random.text_gen(len_max=100), type_finish_date=1)
        TaskWithStepsFactory.create(name='Task 2 on Project 1', task_list=list1, owner=bill, author=bill, finish_date=date.today(),
                                    type_finish_date=1)
        TaskWithStepsFactory.create(name='Task 3 on Project 1', task_list=list1, owner=bill, author=bill, finish_date=date.today(),
                                    description=random.text_gen(len_max=100), type_finish_date=1)
        TaskWithStepsFactory.create(name='Task 4 on Project 2', task_list=list2, owner=kate, author=bill, finish_date=None,
                                    type_finish_date=None)
        TaskWithStepsFactory.create(name='Task 5 on Project 2', task_list=list2, owner=kate, author=bill, finish_date=None,
                                    type_finish_date=None, description=random.text_gen(len_max=100))
        TaskWithStepsFactory.create(name='Task 6 on Project 2', task_list=list2, owner=kate, author=bill, finish_date=None,
                                    type_finish_date=None)
        TaskWithStepsFactory.create(name='Task 7 on Project 3', task_list=list3, owner=james, author=bill, finish_date=None,
                                    type_finish_date=None, description=random.text_gen(len_max=100))
        TaskWithStepsFactory.create(name='Task 8 on Project 3', task_list=list3, owner=james, author=bill, finish_date=None,
                                    type_finish_date=None)
        TaskWithStepsFactory.create(name='Task 9 on Project 3', task_list=list3, owner=james, author=bill, finish_date=None,
                                    type_finish_date=None, description=random.text_gen(len_max=100))
        TaskWithStepsFactory.create(name='Task 10 on Project 4', task_list=list4, owner=bill, author=kate, finish_date=date.today(),
                                    type_finish_date=1)
        TaskWithStepsFactory.create(name='Task 11 on Project 4', task_list=list4, owner=bill, author=kate, finish_date=date.today(),
                                    description=random.text_gen(len_max=100), type_finish_date=1)
        TaskWithStepsFactory.create(name='Task 12 on Project 4', task_list=list4, owner=bill, author=kate, finish_date=None,
                                    type_finish_date=None)
        TaskWithStepsFactory.create(name='Task 13 on Project 5', task_list=list5, owner=james, author=kate, finish_date=None,
                                    type_finish_date=None, description=random.text_gen(len_max=100))
        TaskWithStepsFactory.create(name='Task 14 on Project 5', task_list=list5, owner=james, author=kate, finish_date=None,
                                    type_finish_date=None)
        TaskWithStepsFactory.create(name='Task 15 on Project 5', task_list=list5, owner=james, author=kate, finish_date=None,
                                    type_finish_date=None, description=random.text_gen(len_max=100))

        #create undone tasks without steps
        self.stdout.write("Starting create undone tasks without steps")
        TaskFactory.create(name='Task 16 on Project 6', task_list=list6, owner=kate, author=kate)
        TaskFactory.create(name='Task 17 on Project 6', task_list=list6, owner=kate, author=kate,
                           description=random.text_gen(len_max=100))
        TaskFactory.create(name='Task 18 on Project 6', task_list=list6, owner=kate, author=kate)
        TaskFactory.create(name='Task 19 on Project 4', task_list=list4, owner=bill, author=james,
                           description=random.text_gen(len_max=100))
        TaskFactory.create(name='Task 20 on Project 4', task_list=list4, owner=bill, author=james,
                           description=random.text_gen(len_max=100))
        TaskFactory.create(name='Task 21 on Project 4', task_list=list4, owner=bill, author=james)
        TaskFactory.create(name='Task 22 on Project 1', task_list=list1, owner=kate, author=james,
                           description=random.text_gen(len_max=100))
        TaskFactory.create(name='Task 23 on Project 1', task_list=list1, owner=kate, author=james)
        TaskFactory.create(name='Task 24 on Project 1', task_list=list1, owner=kate, author=james,
                           description=random.text_gen(len_max=100))
        TaskFactory.create(name='Task 25 on Project 2', task_list=list2, owner=james, author=james)
        TaskFactory.create(name='Task 26 on Project 2', task_list=list2, owner=james, author=james,
                           description=random.text_gen(len_max=100))
        TaskFactory.create(name='Task 27 on Project 2', task_list=list2, owner=james, author=james)

        #create undone tasks with steps and tags

        self.stdout.write("Starting create undone tasks with steps and tags")
        TaskWithTagsAndStepsFactory.create(name='Task 28 on Project 5', task_list=list5, owner=bill, author=bill, finish_date=None,
                                           description=random.text_gen(len_max=200), tags=bill_tags,
                                           estimate_time=0, type_finish_date=None, pinned=True)
        TaskWithTagsAndStepsFactory.create(name='Task 29 on Project 5', task_list=list5, owner=bill, author=bill, finish_date=None,
                                           type_finish_date=None,
                                           tags=bill_tags, estimate_time=0)
        TaskWithTagsAndStepsFactory.create(name='Task 30 on Project 5', task_list=list5, owner=bill, author=bill, finish_date=None,
                                           type_finish_date=None,
                                           description=random.text_gen(len_max=200), tags=bill_tags,
                                           estimate_time=0, pinned=True)
        TaskWithTagsAndStepsFactory.create(name='Task 31 on Project 6', task_list=list6, owner=kate, author=bill, finish_date=None,
                                           type_finish_date=None, tags=kate_tags,
                                           estimate_time=0)
        TaskWithTagsAndStepsFactory.create(name='Task 32 on Project 6', task_list=list6, owner=kate, author=bill, finish_date=None,
                                           type_finish_date=None,
                                           description=random.text_gen(len_max=200), tags=kate_tags,
                                           estimate_time=0, pinned=True)
        TaskWithTagsAndStepsFactory.create(name='Task 33 on Project 6', task_list=list6, owner=kate, author=bill, finish_date=None,
                                           type_finish_date=None, tags=kate_tags, pinned=True)
        TaskWithTagsAndStepsFactory.create(name='Task 34 on Project 3', task_list=list3, owner=james, author=bill, finish_date=None,
                                           type_finish_date=None,
                                           description=random.text_gen(len_max=200), tags=james_tags,
                                           estimate_time=0)
        TaskWithTagsAndStepsFactory.create(name='Task 35 on Project 3', task_list=list3, owner=james, author=bill, finish_date=None,
                                           type_finish_date=None, tags=james_tags)
        TaskWithTagsAndStepsFactory.create(name='Task 36 on Project 3', task_list=list3, owner=james, author=bill, finish_date=None,
                                           type_finish_date=None, description=random.text_gen(len_max=200),
                                           tags=james_tags, estimate_time=0)
        TaskWithTagsAndStepsFactory.create(name='Task 37 on Project 4', task_list=list4, owner=bill, author=kate, finish_date=None, tags=bill_tags,
                                           estimate_time=0, type_finish_date=None, pinned=True)
        TaskWithTagsAndStepsFactory.create(name='Task 38 on Project 4', task_list=list4, owner=bill, author=kate, finish_date=None,
                                           type_finish_date=None, description=random.text_gen(len_max=200),
                                           tags=bill_tags)
        TaskWithTagsAndStepsFactory.create(name='Task 39 on Project 4', task_list=list4, owner=bill, author=kate, finish_date=None,
                                           type_finish_date=None, tags=bill_tags)
        TaskWithTagsAndStepsFactory.create(name='Task 40 on Project 5', task_list=list5, owner=james, author=kate, finish_date=None,
                                           type_finish_date=None, description=random.text_gen(len_max=200),
                                           tags=james_tags)
        TaskWithTagsAndStepsFactory.create(name='Task 41 on Project 5', task_list=list5, owner=james, author=kate, finish_date=None,
                                           type_finish_date=None, tags=james_tags, pinned=True)
        TaskWithTagsAndStepsFactory.create(name='Task 42 on Project 5', task_list=list5, owner=james, author=kate, finish_date=None,
                                           type_finish_date=None, description=random.text_gen(len_max=200),
                                           tags=james_tags)

        next_year = date.today() + timedelta(365)

        #create suspended tasks
        TaskFactory.create(task_list=list1, status=2, owner=bill, author=bill, finish_date=None, suspend_date=next_year,
                           type_finish_date=None)
        TaskFactory.create(task_list=list1, status=2, owner=bill, author=bill, finish_date=None, type_finish_date=None)
        TaskFactory.create(task_list=list1, status=2, owner=bill, author=bill, finish_date=None, type_finish_date=None)
        TaskFactory.create(task_list=list2, status=2, owner=kate, author=bill, finish_date=None, suspend_date=next_year,
                           type_finish_date=None)
        TaskFactory.create(task_list=list2, status=2, owner=kate, author=bill, finish_date=None, type_finish_date=None)
        TaskFactory.create(task_list=list2, status=2, owner=kate, author=bill, finish_date=None, type_finish_date=None)
        TaskFactory.create(task_list=list3, status=2, owner=james, author=bill, finish_date=None, type_finish_date=None,
                           suspend_date=next_year)
        TaskFactory.create(task_list=list3, status=2, owner=james, author=bill, finish_date=None, type_finish_date=None)
        TaskFactory.create(task_list=list3, status=2, owner=james, author=bill, finish_date=None, type_finish_date=None)

        #fill tasks statistics
        for arg in range(30):
            TaskStatistics.add_statistics(user=bill, delta_tasks=2, estimate_time=5*arg, spend_time=7*arg,
                                      date=timezone.now() - timezone.timedelta(days=30) + timezone.timedelta(days=arg))