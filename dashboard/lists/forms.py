#-*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from django import forms
from django.core.exceptions import ValidationError
from .models import List, ShareListPending
from commons.forms import CreateModelForm


class ListCreateForm(CreateModelForm):
    name = forms.CharField(label=_("name"), required=True,
                               error_messages={'required': "List name is required."})

    class Meta:
        model = List
        exclude = ["modification_date"]


class ListEditForm(forms.ModelForm):
    name = forms.CharField(label=_("name"), required=True,
                               error_messages={'required': "List name is required."})

    class Meta:
        model = List
        exclude = ['modification_date']

    def __init__(self, data, *args, **kwargs):
        data['share_with'] = [user['id'] if 'id' in user else user['email'] for user in data['share_with']]
        super(ListEditForm, self).__init__(data, *args, **kwargs)


    # def clean_share_with(self):
    #     for user in self.cleaned_data['share_with']:
    #         for mate in self.cleaned_data['share_with']:
    #             if not Team.is_team_mate(user.id, mate.id):
    #                 raise forms.ValidationError(_("Not team mate in share with list"))
    #         if not Team.is_team_mate(self.cleaned_data['owner'].id, user.id):
    #             raise forms.ValidationError(_("Not team mate in share with list"))
    #     return self.cleaned_data['share_with']

    def clean_ancestor(self):
        if self.cleaned_data['ancestor'] and self.cleaned_data['ancestor'].is_inbox:
            raise forms.ValidationError(_("Inbox cannnot have sublist"))
        return self.cleaned_data['ancestor']

    def clean(self):
        self.cleaned_data = super(ListEditForm, self).clean()
        if 'share_with' in self.cleaned_data and (not self.cleaned_data['share_with'] or self.cleaned_data['share_with'] == []):
            self.cleaned_data['share_with'] = [self.instance.owner.id]

        return self.cleaned_data


class ListDeleteForm(forms.Form):
    pk = forms.IntegerField()

    def __init__(self, data, user=None, instance=None, *args, **kwargs):
        self.instance = instance
        self.user = user
        super(ListDeleteForm, self).__init__(data, *args, **kwargs)

    def clean(self):
        if self.instance.is_inbox:
            raise forms.ValidationError(_("You cannot delete inbox."))
        if self.user in self.instance.share_with.all():
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("You don't have permission to delete this list."))


class ShareWithPendingForm(forms.ModelForm):

    class Meta:
        model = ShareListPending
        fields = ["user", "email", "list", "is_active"]
