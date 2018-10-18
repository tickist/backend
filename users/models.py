#-*- coding: utf-8 -*-
import datetime
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, UserManager, AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from commons.utils import polish_string, DEFAULT_TASK_VIEW
from dashboard.lists.models import List, ShareListPending
from commons.utils import disable_for_loaddata

from .utils import create_thumbnail


def get_path(user, name):
    """
        Path for an upload file
    """
    dir = "users/%d/%s" % (name[0], polish_string(name[1]))
    return dir

ORDER_TASKS_DASHBOARD = [('Today->Overdue', "Today->Overdue"),
                         ("Overdue->Today", "Overdue->Today")]

OVERDUE_TASKS_SORT_BY_OPTIONS = [('{"fields": ["priority", "finishDate", "finishTime", "name"], '
                                  '"orders": ["asc", "asc", "asc", "asc"]}', 'priority, finishDate, name'),
                                 ('{"fields": ["priority", "finishDate", "finishTime", "name"], '
                                  '"orders": ["asc", "desc", "desc", "asc"]}', 'priority, -finishDate, name')]

FUTURE_TASKS_SORT_BY_OPTIONS = [('{"fields": ["finishDate", "finishTime", "name"], '
                                 '"orders": ["desc", "asc", "asc"]}', 'finishDate, finishTime, name'),
                                 ('{"fields": ["priority", "finishDate", "finishTime", "name"], '
                                 '"orders": ["asc", "desc", "asc", "asc"]}', 'priority, finishDate, finishTime, name'),
                                ('{"fields": ["finishDate", "finishTime", "name"], '
                                 '"orders": ["asc", "desc", "asc"]}', '-finishDate, finishTime, name')]


class User(AbstractUser):
    """
        Moja klasa użytkownika
    """

    email = models.EmailField(max_length=100, unique=True, db_index=True)
    username = models.CharField(max_length=100, db_index=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True, editable=False, blank=True, null=True, )
    avatar = models.ImageField(upload_to=get_path, default=settings.DEFAULT_AVATAR)
    is_confirm_email = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    registration_key = models.CharField(db_index=True, max_length=60, null=True, blank=True)
    #notifications options
    daily_summary_hour = models.TimeField(blank=True, null=True)
    removes_me_from_shared_list = models.BooleanField(default=True)
    shares_list_with_me = models.BooleanField(default=True)
    assigns_task_to_me = models.BooleanField(default=True)
    completes_task_from_shared_list = models.BooleanField(default=True)
    changes_task_from_shared_list_that_is_assigned_to_me = models.BooleanField(default=True)
    changes_task_from_shared_list_that_i_assigned_to_him_her = models.BooleanField(default=True)
    leaves_shared_list = models.BooleanField(default=True)
    deletes_list_shared_with_me = models.BooleanField(default=True)
    #options
    order_tasks_dashboard = models.CharField(max_length=40, choices=ORDER_TASKS_DASHBOARD,
                                             default="Today->Overdue")
    default_task_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='extended')
    all_tasks_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='simple')
    default_task_view_today_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='extended')
    default_task_view_overdue_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='extended')
    default_task_view_future_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='simple')
    default_task_view_tags_view = models.CharField(max_length=40, choices=DEFAULT_TASK_VIEW, default='extended')
    dialog_time_when_task_finished_in_project = models.BooleanField(default=False)
    overdue_tasks_sort_by = models.CharField(max_length=100, choices=OVERDUE_TASKS_SORT_BY_OPTIONS,
                                             default=OVERDUE_TASKS_SORT_BY_OPTIONS[0][0])
    future_tasks_sort_by = models.CharField(max_length=200, choices=FUTURE_TASKS_SORT_BY_OPTIONS,
                                            default=FUTURE_TASKS_SORT_BY_OPTIONS[0][0])
    projects_filter_id = models.IntegerField(default=1)
    tags_filter_id = models.IntegerField(default=1)
    is_authenticated = True
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []
    GOOGLE_CLASS_NAMES = ['GoogleOpenId', 'google-oauth', 'google-oauth', 'GooglePlusAuth']
    FACEBOOK_CLASS_NAMES = ['FacebookOAuth2', 'facebook']
    objects = UserManager()

    def __unicode__(self):
        return self.email

    def is_notification_codename_send(self, codename):
        return getattr(self, codename)

    def get_full_name(self):
        """
            Return username of the user
        """
        return self.username

    def get_absolute_url(self):
        """
            Return absolute url of the user
        """
        return reverse("user-detail")

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True

    def has_module_perms(self, app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True

    def delete(self, *args, **kwargs):
        """
            Funkcja nadpisuja funkcję usuwającą obiekt z bazy danych
        """
        self.is_active = False
        self.save()

    def _generate_active_key(self):
        import hashlib
        key = "ADFGUEDSE12345#$!#%^@^#&BFmifdsjfiskdoakdposkanfsruehunvushfu,./;[]"
        active_key = hashlib.md5()
        active_key.update(key.encode("utf8"))
        active_key.update(self.username.encode("utf8") + self.password.encode("utf8"))
        return active_key.hexdigest()

    @property
    def all_lists_pk(self):
        """
            Function returns all primary keys users list
        """
        return List.objects.prefetch_related("share_with").filter(share_with=self, is_active=True).values_list("id", flat=True)

    @property
    def active(self):
        return self.is_active

    @property
    def inbox_pk(self):
        """
            Function returns user inbox pk
        """
        return List.objects.get(owner=self, is_inbox=True).pk

    def get_inbox(self):
        """
            Function returns user inbox pk
        """
        return List.objects.get(owner=self, is_inbox=True)

    def facebook_connection(self):
        """
            If user account is connection with facebook account the function returns id of association
            else the function returns false
        """
        user_socials = UserSocialAuth.objects.filter(user=self)
        for user_social in user_socials:
            if user_social.get_backend().__name__ in self.FACEBOOK_CLASS_NAMES and user_social.user_exists():
                return user_social.id
        return False

    def google_connection(self):
        """
            If user account is connection with google account the function returns id of association
            else the function returns false
        """
        user_socials = UserSocialAuth.objects.filter(user=self)
        for user_social in user_socials:
            if user_social.get_backend().__name__ in self.GOOGLE_CLASS_NAMES and user_social.user_exists():
                return user_social.id
        return False

    @property
    def inbox(self):
        """
            Function returns user inbox object
        """
        return List.objects.get(owner=self, is_inbox=True)

    @staticmethod
    def get_user_from_email(email):
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            user = None
        return user

    def avatar_delete(self):
        """ Function to delete old avatar """

        self.avatar = settings.DEFAULT_AVATAR
        self.save()

    def avatar_save(self, photo):
        """
            Add new avatar
        """
        path = [self.id, photo.name]
        self.avatar_delete()
        self.avatar.save(path, photo)
        self.save()
        create_thumbnail(self.avatar.name, self.id)

    def avatar_url(self):
        """
            Function returns avatar url
        """
        if self.avatar.name.find("default_avatar_user") >= 0:
            url = '/' + self.avatar.name
        else:
            url = '/media/' + self.avatar.name
        return url

    def save(self, *args, **kwargs):
        if not self.registration_key:
            self.registration_key = self._generate_active_key()
        super(User, self).save(*args, **kwargs)

    def is_team_mate(self, user1):
        try:
            user1 = int(user1)
        except ValueError:
            return False
        if user1 == self.id:
            return True
        else:
            all_team_mate = self.all_team_mates()
            all_team_mate = [x.id for x in all_team_mate]
            if user1 in all_team_mate:
                return True
        return False

    def all_team_mates(self):
        return User.objects.filter(share_with__in=self.all_lists_pk).exclude(id=self.id).distinct()

    def all_team_mates_and_self(self):
        return User.objects.filter(share_with__in = self.all_lists_pk).distinct()


class Message(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, related_name="user_message",  on_delete=models.DO_NOTHING)


@receiver(post_save, sender=User)
@disable_for_loaddata
def creating_inbox_tasks_tags_after_user_save(sender, instance, created, *args, **kwargs):
    if created:
        from django.utils.translation import ugettext as _
        from dashboard.tasks.models import Task, Tag
        for name in [_("work"), _("home"), _("need focus"), _("someday/maybe"), _("tasks for later"),
                     _('quick tasks'), _('getting to know Tickist')]:
            try:
                Tag.objects.get(name=name, author=instance)
            except Tag.DoesNotExist:
                Tag(name=name, author=instance).save()
        list_name = _("Inbox")
        try:
             project = List.objects.get(name=list_name, owner=instance)
        except List.DoesNotExist:
            project = List()
            project.name = list_name
            project.owner = instance
            project.is_inbox = True
            project.save()
            project.share_with.add(instance)
        task1 = Task()
        task1.name = ('Find out more about Tickist')
        task1.author = instance
        task1.owner = instance
        task1.finish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        task1.task_list = project
        task1.estimate_time = 5
        task1.save()
        task1.tags.add(Tag.objects.get(name = _('getting to know Tickist'), author=instance))
        task1.tags.add(Tag.objects.get(name = _('quick tasks'), author=instance))

        task2 = Task()
        task2.name = ('Find out more about editing tasks')
        task2.author = instance
        task2.owner = instance
        task2.task_list = project
        task2.finish_date = datetime.datetime.now().strftime('%Y-%m-%d')
        task2.estimate_time = 5
        task2.save()
        task2.tags.add(Tag.objects.get(name=_('getting to know Tickist'), author=instance))
        task2.tags.add(Tag.objects.get(name=_('quick tasks'), author=instance))


@receiver(post_save, sender=User)
@disable_for_loaddata
def remove_pending_user(sender, instance, created, *args, **kwargs):
    if created:
        sharing_pending = ShareListPending.objects.filter(email=instance.email, is_active=True)
        for arg in sharing_pending:
            arg.list.share_with.add(instance)
            arg.is_active = False
