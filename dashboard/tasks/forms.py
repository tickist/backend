#-*- coding: utf-8 -*-

import re
from django import forms
import dateutil.parser
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.db.models.fields import NOT_PROVIDED
from django.utils.datastructures import MultiValueDictKeyError
from isodate import parse_date
from commons.forms import CreateModelForm
from .models import Task, TaskStep, Tag
from .mixins import ValidationTimeMixin


class TaskCreateForm(CreateModelForm, ValidationTimeMixin):
    name = forms.CharField(label=_("name"), required=True,
                               error_messages={'required': "Task name is required.",
                                               'max_length': "Task name is too long (%(show_value)d characters). Maximum %(limit_value)d characters are allowed."})
    estimate_time = forms.CharField(max_length=200, required=False)
    time = forms.CharField(max_length=200, required=False)

    class Meta:
        model = Task
        exclude = ["modification_date"]

    def __init__(self, data, *args, **kwargs):
        tags = []
        data['task_list'] = data['task_project']
        if 'finish_date' in data and data['finish_date']:
            data.update(
                {'finish_date': dateutil.parser.parse(data['finish_date']).strftime('%d-%m-%Y')})
        if 'owner' in data and isinstance(data['owner'], dict):
            data.update({"owner": data['owner']['id']})
        if 'task_list' in data and isinstance(data['task_list'], dict):
            data.update({"task_list": data['task_list']['id']})

        if 'tags' in data:
            for tag in data['tags']:
                if isinstance(tag, dict):
                    tag = tag['id']
                tags.append(tag)
        data.update({"tags": tags})
        super(TaskCreateForm, self).__init__(data, *args, **kwargs)


    def clean_time(self):
        return self._validate_time(self.cleaned_data['time'])

    def clean_estimate_time(self):
        return self._validate_time(self.cleaned_data['estimate_time'])

    def clean(self):
        if self.cleaned_data['owner'] not in self.cleaned_data['task_list'].share_with.all():
            raise forms.ValidationError(_("This user is not in your team"))
        return self.cleaned_data


class TaskEditForm(forms.ModelForm, ValidationTimeMixin):
    name = forms.CharField(label=_("name"), required=True,
                               error_messages={'required': "Task name is required.",
                                               'max_length': "Task name is too long (%(show_value)d characters). Maximum %(limit_value)d characters are allowed."})
    estimate_time = forms.CharField(max_length=200, required=False)
    time = forms.CharField(max_length=200, required=False)

    class Meta:
        model = Task
        exclude = ['modification_date', 'id']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("user", None)
        kwargs.pop('user')
        # TODO remove it when we changed list to project
        kwargs['data']['task_list'] = kwargs['data']['task_project']
        if 'task_list' in kwargs['data'] and isinstance(kwargs['data']['task_list'], dict):
            kwargs['data'].update({"task_list": kwargs['data']['task_list']['id']})
        if 'owner' in kwargs['data'] and isinstance(kwargs['data']['owner'], dict):
            kwargs['data'].update({"owner": kwargs['data']['owner']['id']})
        if 'author' in kwargs['data'] and isinstance(kwargs['data']['author'], dict):
            kwargs['data'].update({"author": kwargs['data']['author']['id']})
        tags = []
        if 'finish_date' in kwargs['data'] and kwargs['data']['finish_date']:
            kwargs['data'].update({'finish_date': dateutil.parser.parse(kwargs['data']['finish_date']).strftime('%d-%m-%Y')})
        if 'suspend_date' in kwargs['data'] and kwargs['data']['suspend_date']:
            kwargs['data'].update({'suspend_date': dateutil.parser.parse(kwargs['data']['suspend_date']).strftime('%d-%m-%Y')})
        if 'tags' in kwargs['data']:
            for tag in kwargs['data']['tags']:
                if isinstance(tag, dict):
                    tag = tag['id']
                tags.append(tag)
        kwargs['data'].update({"tags": tags})
        super(TaskEditForm, self).__init__(*args, **kwargs)

    def clean(self):

        if self.cleaned_data['owner'] not in self.cleaned_data['task_list'].share_with.all():
            raise forms.ValidationError(_("This user is not in your team"))

        if 'status' in self.cleaned_data and self.cleaned_data['status'] != 2:
            del self.cleaned_data['suspend_date']
        return self.cleaned_data

    def clean_tags(self):
        for tag in self.cleaned_data['tags']:
            if tag.author.pk != self.user.pk:
                raise forms.ValidationError(_("You dont have permission to add tag %s" % tag.name))
        #adding tags from another users
        return self.cleaned_data['tags'] | self.instance.tags.exclude(author__pk=self.user.pk)

    def clean_time(self):
        return self._validate_time(self.cleaned_data['time'])

    def clean_estimate_time(self):
        return self._validate_time(self.cleaned_data['estimate_time'])


class TaskStepFormCreate(forms.ModelForm):

    class Meta:
        model = TaskStep
        exclude = ['modification_date', "status", "task"]


class TaskStepFormEdit(forms.ModelForm):

    class Meta:
        model = TaskStep
        exclude = ['modification_date', "task"]


class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        exclude = ['modification_date']

    def __init__(self, data, user=None, *args, **kwargs):
        self.user = user
        if user and not'author' in data:
            data = data.copy()
            data.update({"author": user})
        super(TagForm, self).__init__(data, *args, **kwargs)

    def clean(self):
        if hasattr(self.instance, "author") and self.instance.author.pk != self.user:
            raise forms.ValidationError(_("You don't have permissions to delete this tag "))
        return self.cleaned_data


class TaskDeleteForm(forms.Form):
    pk = forms.IntegerField()

    def __init__(self, data, user=None, instance=None, *args, **kwargs):
        self.instance = instance
        self.user = user
        super(TaskDeleteForm, self).__init__(data, *args, **kwargs)

    def clean(self):
        if self.user == self.instance.owner:
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("You don't have permission to delete this task."))