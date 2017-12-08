# -*- coding: utf-8 -*-

from datetime import date, timedelta
from random import choice
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from mptt.models import MPTTModel, TreeForeignKey
from commons.utils import polish_string, DEFAULT_TASK_VIEW


color_list = [("#6be494", "#6be494"),
              ("#f3d749", "#f3d749"),
              ("#fcb150", "#fcb150"),
              ("#f3df9a", "#f3df9a"),
              ("#b6926e", "#b6926e"),
              ("#4fc4f6", "#4fc4f6"),
              ("#367cdc", "#367cdc"),
              ("#b679b2", "#b679b2"),
              ("#be5753", "#be5753"),
              ("#fb7087", "#fb7087"),
]

choices_priority = [('A', "A"), ("B", "B"), ("C", "C")]
choices_type_finish_date = [[0, _("by")], [1, _("on")]]
choices_default_finish_date = [[0, 'today'], [1, 'tomorrow'], [2, 'next week']]


def get_path(user, name):
    my_dir = "files/users/%d/%s" % (name[0], polish_string(name[1]))
    return my_dir


class List(MPTTModel):
    """
        Model listy
    """

    name = models.CharField(max_length=40)
    description = models.TextField(max_length=400, default="", blank=True, null=True)
    logo = models.ImageField(upload_to=get_path, default=settings.DEFAULT_LIST_LOGO)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner_list",  on_delete=models.DO_NOTHING)
    is_inbox = models.BooleanField(default=False)  # default list
    share_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="share_with", blank=True)
    ancestor = TreeForeignKey('self', null=True, blank=True, related_name='children',  on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(editable=False, auto_now=True)
    color = models.CharField(default=settings.DEFAULT_COLOR_LIST, max_length=100)
    is_active = models.BooleanField(default=True)
    #list rules
    default_priority = models.CharField(choices=choices_priority, default="C", max_length=1)
    default_finish_date = models.IntegerField(choices=choices_default_finish_date, null=True, blank=True)
    default_type_finish_date = models.IntegerField(choices=choices_type_finish_date, null=True, blank=True)
    default_task_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='extended')

    class MPTTMeta:
        parent_attr = "ancestor"
        order_insertion_by = ["-is_inbox", "name"]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_descendants(self):
        """
            Pobranie wszystkich list, które bezpośrednio podlegają liście głównej
        """
        lists = self.get_descendants_obj()
        lists = lists.values("id")
        mylist = []
        for tmp_list in lists:
            mylist.append(tmp_list['id'])
        return mylist

    @classmethod
    def create_notification(cls, request, old_list=None, old_share_with=None, new_list=None, new_share_with=None,
                            form=None):
        from notifications.tasks import create_notification

        if not old_share_with:
            old_share_with = []
        else:
            old_share_with = list(old_share_with)
        if not new_share_with:
            new_share_with = []
        else:
            new_share_with = list(new_share_with)
        if old_share_with != new_share_with:
            if old_list and new_list and old_list.is_active and not new_list.is_active:
                for user in old_share_with:
                    if user != request.user:
                        codename = "deletes_list_shared_with_me"
                        create_notification(codename, new_list, {'author_username': user.username,
                                                                 'author_email': user.email, 'list_name': new_list.name},
                                            recipients=[user])
            else:
                for user in old_share_with:
                    if user not in new_share_with:
                        if user == request.user:
                            codename = "leaves_shared_list"
                            create_notification(codename, new_list,
                                                {'author_username': user.username, 'author_email': user.email,
                                                 'list_name': new_list.name}, recipients=new_share_with)
                        else:
                            codename = "removes_me_from_shared_list"
                            create_notification(codename, new_list, {'author_username': request.user.username,
                                                                     'author_email': request.user.email, 'list_name': new_list.name}, recipients=[user])
                for user in new_share_with:
                    if user not in old_share_with and user != request.user:
                        codename = "shares_list_with_me"
                        create_notification(codename, new_list,
                                            {'author_username': request.user.username,
                                             'author_email': request.user.email, 'list_name': new_list.name},
                                            recipients=[user])


    def tasks_counter(self):
        from dashboard.tasks.models import Task

        return Task.objects.filter(status=0, task_list__in=self.get_all_descendants(), is_active=True).count()

    def get_all_descendants(self):
        descendants = [self.id]
        for l in self.get_descendants_obj():
            descendants.append(l.id)
            for ll in l.get_descendants_obj():
                descendants.append(ll.id)
        return descendants

    def get_descendants_obj(self, user=None):
        filters = {"ancestor__id": self.id}
        if user:
            filters['share_with'] = user
        return List.objects.filter(**filters)

    def get_serialized_descendants(self, user=None, request=None):
        serialized = []
        from .serializers import ListSerializer

        lists = self.get_descendants_obj(user)
        for my_list in lists:
            serialized.append(ListSerializer(my_list, context={"request": request}).data)

        return serialized

    def get_tags(self, user=None):
        from dashboard.tasks.models import Task, Tag

        tasks = Task.objects.filter(owner=user, task_list__in=self.get_all_descendants()).values_list("id", flat=True)
        return Tag.objects.filter(task__in=tasks).distinct().values("id", "name", "author")

    def is_shared_with_user(self, user):
        return List.objects.filter(id=self.pk, share_with=user).exists()

    def task_finish_date(self):
        """
        Function returns default task finish date
        """
        task_date = None
        if self.default_finish_date == 0:
            task_date = date.today()
        elif self.default_finish_date == 1:
            task_date = date.today() + timedelta(1)
        elif self.default_finish_date == 2:
            task_date = date.today() + timedelta(7)
        if task_date:
            task_date = task_date.strftime("%d-%m-%Y")
        return task_date

    def save(self, *args, **kwargs):
        super(List, self).save(*args, **kwargs)


class ShareListPending(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="invite_another_user", on_delete=models.CASCADE)
    email = models.EmailField()
    list = models.ForeignKey(List, null=True, blank=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email
