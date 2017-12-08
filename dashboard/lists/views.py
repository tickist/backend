#-*- coding: utf-8 -*-

from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.db.models import Q
from rest_framework import permissions
from rest_framework import generics, viewsets, views
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import list_route, detail_route

from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from dashboard.lists.serializers import ListSerializer, SimpleListSerializer
from dashboard.lists.models import List, ShareListPending
from dashboard.lists.forms import ShareWithPendingForm
from users.models import User
from users.serializers import SimpleUserSerializer
from .forms import ListCreateForm, ListEditForm, ListDeleteForm
import json



class ListViewSet(viewsets.ModelViewSet):

    serializer_class = ListSerializer
    model = List
    renderer_classes = [JSONRenderer]

    def _child_level_0(self):
        """TR: Function returns lists without ancestor. Jeśli Ancestor nie jest udostępniony to nie istnieje"""
        #TODO Need refactoring (can be to slow)
        all_user_lists = List.objects.filter(share_with=self.request.user.pk, is_active=True).prefetch_related('share_with')
        result = []
        for mylist in all_user_lists:
            if mylist.is_root_node():
                result.append(mylist)
            else:
                is_root_for_user = True
                for ancestor in mylist.get_ancestors():
                    if ancestor.is_shared_with_user(self.request.user):
                        is_root_for_user = False
                if is_root_for_user:
                    result.append(mylist)

        return result

    def get_queryset(self):
        child_level = self.request.query_params.get('child_level', None)
        is_inbox = self.request.query_params.get('is_inbox', None)
        filters = {'share_with': self.request.user.pk}
        if is_inbox:
            filters['is_inbox'] = json.loads(is_inbox)
        if child_level:
            #Tylko listy z pierwszego poziomu
            if child_level == '0':
                filters['ancestor__isnull'] = True
                lists = self._child_level_0()
            #the oldest lists and sons
            if child_level == '1':
                filters['ancestor__ancestor__isnull'] = True
                lists = List.objects.filter(**filters).order_by("-is_inbox", "name").prefetch_related('share_with')
        else:
            lists = List.objects.filter(share_with=self.request.user.pk, is_active=True).prefetch_related('share_with')
        return lists

    def list(self, request, *args, **kwargs):
        simple_lists = self.request.query_params.get('simple_lists', None)
        self.object_list = self.filter_queryset(self.get_queryset())

        if simple_lists:
            result = Response(SimpleListSerializer(self.object_list, many=True).data, status=status.HTTP_200_OK)
        else:
            # Switch between paginated or standard style responses
            page = self.paginate_queryset(self.object_list)
            if page is not None:
                serializer = self.get_pagination_serializer(page)
            else:
                serializer = self.get_serializer(self.object_list, many=True)
            result = Response(serializer.data)
        return result

    def create(self, request):
        data = self._save_and_remove_pending_users(request.data.copy())
        data['owner'] = request.user.pk
        form = ListCreateForm(data)
        if form.is_valid():
            mylist = form.save()
            mylist.share_with.add(mylist.owner)
            for arg in ShareListPending.objects.filter(is_active=True, user=self.request.user, list__isnull=True):
                arg.list = mylist
                arg.save()
            data = ListSerializer(mylist).data
            data["message"] = _("List has been saved successfully.")
            List.create_notification(form=form, new_list=mylist, request=request, new_share_with=mylist.share_with.all())
            result = Response(data, status=status.HTTP_201_CREATED)
        else:
            result = Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return result

    def _save_and_remove_pending_users(self, data, my_list=None):
        if 'share_with' in data:
            if my_list:
                ShareListPending.objects.filter(list=my_list, is_active=True).delete()
            data_share_with_tmp = data['share_with'].copy()
            for arg in data['share_with']:
                if 'id' not in arg:
                    try:
                        validate_email(arg['email'])
                    except ValidationError:
                        pass
                    else:
                        share_list_pending, create = ShareListPending.objects.get_or_create(user=self.request.user,
                                                                                            email=arg['email'],
                                                                                            is_active=True)
                        if my_list:
                            share_list_pending.list = my_list
                            share_list_pending.save()

                        data_share_with_tmp.remove(arg)
            data['share_with'] = data_share_with_tmp
        return data

    @detail_route(methods=["get"])
    def sharewithlist(self, request, pk=None):
        objs = User.objects.filter(share_with=List.objects.get(id=pk))
        data = SimpleUserSerializer(objs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @detail_route(methods=["get"])
    def sublists(self, request, pk=None):
        objs = List.objects.filter(ancestor__id=pk)
        data = SimpleListSerializer(objs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def get_object(self):
        obj = List.objects.select_related('owner', 'ancestor').get(pk=self.kwargs['pk'])
        return obj

    def update(self, request, pk, format=None):
        my_old_list = self.get_object()
        old_share_with = list(my_old_list.share_with.all())
        data = self._save_and_remove_pending_users(request.data.copy(), my_list=my_old_list)
        form = ListEditForm(instance=self.get_object(), data=data)
        if form.is_valid():
            my_list = form.save()
            my_list.share_with.add(request.user)
            data = ListSerializer(my_list).data
            data["message"] = _("List has been changed successfully.")
            List.create_notification(form=form, old_list=my_old_list, new_list=my_list, request=request,
                                     old_share_with=old_share_with, new_share_with=my_list.share_with.all())
            return Response(data, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        my_old_list = self.get_object()
        my_list = self.get_object()
        old_share_with = list(my_list.share_with.all())
        form = ListDeleteForm(user=request.user, instance=my_list, data=self.kwargs)
        if form.is_valid():
            from dashboard.tasks.models import Task
            if my_list.owner == self.request.user:
                for task in Task.objects.filter(task_list=my_list, is_active=True):
                    if self.request.user == my_list.owner.pk:
                        task.is_active = False
                    else:
                        task.task_list = task.owner.get_inbox()
                    task.save()
                my_list.is_active = False
                my_list.save()
                message = _('List has been deleted successfully.')
            else:
                my_list.share_with.remove(self.request.user)
                inbox = self.request.user.get_inbox()
                for task in Task.objects.filter(task_list=my_list, is_active=True, owner=self.request.user):
                    task.is_active = False
                    task.save()
                message = _('You have left the list.')
            List.create_notification(form=form, old_list=my_old_list, new_list=my_list, request=request,
                                     old_share_with=old_share_with, new_share_with=my_list.share_with.all() if my_list.is_active else [])

            return Response({'id': my_list.id, 'message': message}, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_403_FORBIDDEN)
