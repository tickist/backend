#-*- coding: utf-8 -*-

import datetime
from django import forms
from django.utils.translation import ugettext as _
from users.models import User
from django.core.exceptions import ValidationError
from django.conf import settings


class SimpleLoginUserForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(max_length=100)

    def clean(self):
        if not 'email' in self.cleaned_data:
            raise ValidationError(_("Email is not correct."))
        try:
            user = User.objects.get(email=self.cleaned_data['email'])
        except User.DoesNotExist:
            raise ValidationError(_("User does not exist."))
        #check if email and password match
        if not user.check_password(self.cleaned_data['password']):
            raise ValidationError(_("Password and email don't match."))

        if not user.is_active:
            raise ValidationError(_("User is not active."))

        #check if email is confirm (with delay)
        time_confirm_email = datetime.datetime.now() - datetime.timedelta(hours = settings.TIME_TO_CONFIRM_EMAIL)
        if not user.is_confirm_email and user.date_joined < time_confirm_email.date():
            raise ValidationError(_("Email is not confirm"))
        return self.cleaned_data