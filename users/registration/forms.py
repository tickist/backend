#-*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _
from users.models import User
from django.core.exceptions import ValidationError


class SimpleCreateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'password')


    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email, is_active=True).exists():
            return email
        raise ValidationError(_("Sorry, it looks like %s belongs to an existing account." % email))

