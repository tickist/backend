#-*- coding: utf-8 -*-

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.auth import logout, login
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from dashboard.lists.serializers import ListSerializer
from dashboard.lists.models import List
from users.models import User
from users.serializers import UserSerializer
import json
from rest_framework.permissions import AllowAny
from .forms import SimpleLoginUserForm




class SimpleLoginView(generics.GenericAPIView):
    """
    Simple Login Class

    """
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        data = request.data.copy()
        form = SimpleLoginUserForm(data)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            data = self.get_serializer_class()(user).data
            data['message'] = _("User is login")
            result = Response(data, status=status.HTTP_200_OK)
        else:
            result = Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return result


class SimpleLogoutView(generics.GenericAPIView):
    """
    Simple Logout

    """
    serializer_class = UserSerializer

    def get(self, request):
        logout(request) #,  next_page=reverse('news-main'))
        return Response("Logout", status=status.HTTP_200_OK)
