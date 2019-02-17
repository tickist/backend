#-*- coding: utf-8 -*-
import datetime
import factory
from users import models


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.LazyAttribute(lambda o: '%s@tickist.com' % o.username)
    username = factory.Sequence(lambda n: 'james_%d' % n)
    password = "pass"
    daily_summary_hour = "23:59:59"
    last_login = datetime.datetime.now()
    is_confirm_email = True
    is_active = True
    is_superuser = False
    is_staff = False

    class Meta:
        model = models.User
        abstract = False

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', "pass")
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user