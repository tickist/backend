#-*- coding: utf-8 -*-

import factory
from . import models
from users.factory_classes import UserFactory
from users.models import User

class ListFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'List_%d' % n)
    description = "description test"
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = models.List
        abstract = False


    @classmethod
    def _prepare(cls, create, **kwargs):
        mylist = super(ListFactory, cls)._prepare(create, **kwargs)
        if mylist.id:
            mylist.share_with.add(kwargs['owner'])
        return mylist

    @classmethod
    def share_with_count(cls):
        return 2


class ListFactoryShareWithUsers(factory.django.DjangoModelFactory):


    name = factory.Sequence(lambda n: 'List_%d' % n)
    owner = factory.SubFactory(UserFactory)


    class Meta:
        model = models.List
        abstract = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        mylist = super(ListFactoryShareWithUsers, cls)._prepare(create, **kwargs)
        mylist.share_with.add(kwargs['owner'])
        return mylist

    @factory.post_generation
    def share_with(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.share_with.add(group)
