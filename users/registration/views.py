#-*- coding: utf-8 -*-

import json
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from rest_framework import permissions
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from django.views.generic import TemplateView
from django.views.generic.base import View
from users.models import User
from users.serializers import UserSerializer
from commons.utils import send_email_to_admins
from .forms import SimpleCreateUserForm
from emails.utils import async_send_email


class ConfirmEmailView(View):

    @staticmethod
    def send_registration_email(request, user):
        async_send_email.apply_async(kwargs={"topic":_("Thank you for confirmation of your email"), "template":"registration/email/email_confirmation.html",
                   "email": user.email, "data_email": {"user": user}})

    def get(self, request, key):
        user = User.objects.get(registration_key=key)
        user.is_confirm_email = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        self.send_registration_email(request, user)
        login(request, user)
        return HttpResponseRedirect("/")


class SendEmailAfterRegistrationView(View):

    def get(self, request):
        if not request.user.is_confirm_email:
            SimpleRegistrationView.send_registration_email(request, request.user, notification_admin=False)
        return HttpResponseRedirect("/")


class CheckEmailView(generics.GenericAPIView):
    """
    Checking if email is free
    """
    model = User
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data.copy()
        email = data.get("email", None)
        response_object = {}
        if email:
            if not User.objects.filter(email=data['email'], is_active=True).exists():
                response_object['is_taken'] = False
                response_object['messege'] = _(u"Email is free")
            else:
                response_object['is_taken'] = True
                response_object['messege'] = _("Sorry, it looks like %s belongs to an existing account." % email)
        else:
            response_object['is_taken'] = False
            response_object['messege'] = _(u"Please send an email to check")

        return Response(response_object, status=status.HTTP_200_OK)

class SimpleRegistrationView(generics.CreateAPIView):
    """
    Simple Registration

    """
    permission_classes = (AllowAny,)

    @staticmethod
    def send_registration_email(request, user, notification_admin=True):
        registration_key_url = reverse("registration-confirm_email", args=[user.registration_key])
        async_send_email.apply_async(kwargs={"topic":_("Thank you for registering with Tickist!"), "template": "registration/email/registration_email.html",
                   "email": user.email, "data_email": {"registration_key_url": registration_key_url, "user": user},
                   "user": user})
        if notification_admin:
            send_email_to_admins(topic=_("New user %s" % user.email), template="registration/email/new_user_notification_for_admin.html", data={"user": user})

    def post(self, request):
        data = request.data.copy()
        form = SimpleCreateUserForm(data)
        if form.is_valid():

            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            self.send_registration_email(self.request, user)
            # JWT login
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            result = Response({'token': token, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        else:
            result = Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return result



