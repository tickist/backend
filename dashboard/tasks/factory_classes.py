import factory
from random import randint
from . import models
from users.factory_classes import UserFactory
from dashboard.lists.factory_classes import ListFactory
from datetime import date, timedelta


class TaskFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'Task_%d' % n)
    owner = factory.SubFactory(UserFactory)
    author = factory.SubFactory(UserFactory)
    task_list = factory.SubFactory(ListFactory)
    status = 0
    finish_date = date.today() + timedelta(4)
    type_finish_date = 0
    estimate_time = randint(100, 250)
    is_active = True

    class Meta:
        model = models.Task
        abstract = False


class StepFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Task step %d' % n)

    class Meta:
        model = models.TaskStep
        abstract = False


class TagFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: '%d' % n)

    class Meta:
        model = models.Tag
        abstract = False

class TaskWithStepsFactory(TaskFactory):

    @classmethod
    def _prepare(cls, create, **kwargs):
        task = super(TaskWithStepsFactory, cls)._prepare(create, **kwargs)
        if task.id:
            for i in range(5):
                StepFactory(task=task, author=task.owner, order=i)
        return task


class TaskWithTagsAndStepsFactory(TaskWithStepsFactory):
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them

            for group in extracted:
                self.tags.add(group)