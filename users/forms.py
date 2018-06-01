#-*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from .models import User, Message
from django.core.exceptions import ValidationError
from django.db.models import Q


class AddingTeamMate(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, data, user=None, *args, **kwargs):
        self.user = user
        super(AddingTeamMate, self).__init__(data, *args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.get_user_from_email(email)
        if user:
            team_count = Team.objects.filter(Q(user1__pk=self.user.pk, user2__pk=user.pk) |
                                        Q(user1__pk=user.pk, user2__pk=self.user.pk)).count()
            if team_count > 0:
                raise ValidationError(_("This user is in your team."))
        else:
            raise ValidationError(_("User does not have an account in Tickist."))
        return email


class DeleteTeamMate(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, data, user=None, *args, **kwargs):
        self.user = user
        super(DeleteTeamMate, self).__init__(data, *args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.get_user_from_email(email)
        try:
            Team.objects.get(Q(user1__pk=self.user.pk, user2__pk=user.pk) |
                             Q(user1__pk=user.pk, user2__pk=self.user.pk))
        except Team.DoesNotExist:
            raise ValidationError(_("Team mate does not exist"))
        return email


class ChangePasswordForm(forms.Form):
    """
        Form for password change

    """

    password = forms.CharField(required=True)
    new_password = forms.CharField(required=True)
    repeat_new_password = forms.CharField(required=True)

    def __init__(self, data, user=None, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(data, *args, **kwargs)

    def clean_password(self):
        """
            Password validation
        """
        if not self.user.check_password(self.cleaned_data['password']):
            raise ValidationError(_("Password is not corrent."))
        return self.cleaned_data['password']

    def clean(self):
        """
            Check if new password and repeat new password are the same.
        """
        if 'new_password' in self.cleaned_data and 'repeat_new_password' in self.cleaned_data \
                and self.cleaned_data['new_password'] != self.cleaned_data['repeat_new_password']:
            raise ValidationError(_("New password and repeat new password don't match."))
        if 'new_password' in self.cleaned_data and self.cleaned_data['new_password'] == "":
            raise ValidationError(_("New password cannot be blank."))
        return self.cleaned_data


class ChangeUserDetailsForm(forms.ModelForm):
    """
        Change user details form

    """
    username = forms.CharField(label=_("username"), required=True,
                               error_messages={'required': "Username field is required."})

    class Meta:
        model = User
        fields = ("username", "email", "daily_summary_hour", "removes_me_from_shared_list",
                  "shares_list_with_me", "assigns_task_to_me", "completes_task_from_shared_list",
                  "changes_task_from_shared_list_that_is_assigned_to_me", "all_tasks_view",
                  "changes_task_from_shared_list_that_i_assigned_to_him_her", "leaves_shared_list",
                  "default_task_view_today_view", "default_task_view_overdue_view", "default_task_view_future_view",
                  "default_task_view_tags_view", "default_task_view", "overdue_tasks_sort_by", "future_tasks_sort_by",
                  "projects_filter_id", "tags_filter_id")


class SendMessegaToBoardForm(forms.ModelForm):
    """
        Send message to board

    """
    class Meta:
        model = Message
        fields = ['message', 'user']


class ChangeAvatarForm(forms.Form):
    """
        Send message to board

    """
    file = forms.ImageField()


class ForgotPasswordForm(forms.Form):
    """
        Form validation email. This form is used when user forgot password
    """
    email = forms.EmailField(label=_("email"), required=True,
                               error_messages={'required': "Email field is required."})

    def clean_email(self):
        """
            Validation email
        """
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise forms.ValidationError(_('We could not find an account with that email address. '
                                          'Please try again and enter your email:'))
        return email
