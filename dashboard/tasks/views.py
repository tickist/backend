#-*- coding: utf-8 -*-
import json
import time
from datetime import datetime, date
from django.template.response import TemplateResponse
from django.core.signals import request_finished, request_started
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.forms.models import modelformset_factory, inlineformset_factory
from rest_framework import generics, exceptions, permissions
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from dashboard.tasks.serializers import TaskSerializer
from dashboard.tasks.models import Task, TaskStep, Tag
from dashboard.lists.models import List
from users.models import User
from .forms import TaskEditForm, TaskCreateForm, TaskStepFormCreate, TaskStepFormEdit, TaskDeleteForm
from commons.utils import is_number, my_bool
from .utils import FiltersTagMixin



class TasksView(generics.ListCreateAPIView, FiltersTagMixin):
    """
    Widok do wyswietlania listy list
    """
    model = Task
    serializer_class = TaskSerializer
    renderer_classes = [JSONRenderer]

    def recursive_tasks_from_lists(self, **filters):
        #TODO wymaga refaktoringu
        mylist = filters.get("task_list")
        self.obj = Task.objects.filter(**filters) | self.obj
        for arg in mylist.get_descendants_obj():
            self.recursive_tasks_from_lists(**{"task_list": arg})

    def dispatch(self, request, *args, **kwargs):
        global dispatch_time
        global render_time
        dispatch_start = time.time()
        ret = super(TasksView, self).dispatch(request, *args, **kwargs)

        render_start = time.time()
        ret.render()
        render_time = time.time() - render_start

        dispatch_time = time.time() - dispatch_start

        return ret


    def get_queryset(self):
        #TODO wymaga refaktoryzacji
        global serializer_time
        global db_time
        db_start = time.time()

        self.tag_list_ids = Tag.objects.filter(author__pk=self.request.user.pk).values_list("id", flat=True)

        tasks_from_list = self.request.query_params.get('list', None)
        status = self.request.query_params.getlist('status', None)
        orders = self.request.query_params.getlist('o', None)
        tags = self.request.query_params.getlist('tags', None)
        assigned = self.request.query_params.get("assign", None)
        type_finish_date = self.request.query_params.get("type_finish_date", None)
        finish_date = self.request.query_params.get("finish_date")
        finish_date__gt = self.request.query_params.get("finish_date__gt")
        finish_date__lt = self.request.query_params.get("finish_date__lt")
        estimate_time = self.request.query_params.get("estimate_time", None)
        estimate_time__gt = self.request.query_params.get("estimate_time__gt", None)
        estimate_time__lt = self.request.query_params.get("estimate_time__lt", None)
        pinned = my_bool(self.request.query_params.get("pinned", None))

        filters = {}

        if tasks_from_list and is_number(tasks_from_list) and tasks_from_list != "all":
            #create empty queryset
            self.obj = Task.objects.none()
            mylist = get_object_or_404(List, pk=tasks_from_list)
            if not mylist.is_shared_with_user(self.request.user):
                raise exceptions.PermissionDenied
            self.recursive_tasks_from_lists(**{'task_list': mylist}) #this line change self.obj
        else:
            self.obj = Task.objects.select_related("task_list", "owner", "author").filter(task_list__in=self.request.user.all_lists_pk)
        if finish_date:
            if finish_date == "null":
                filters['finish_date__isnull'] = True
            elif pinned is not None and pinned and finish_date == date.today().strftime("%Y-%m-%d"):
                self.obj = self.obj.filter(Q(finish_date=finish_date) | Q(pinned=True))

            else:
                filters['finish_date'] = finish_date
        if finish_date__gt:
            if pinned is not None and not pinned:
                filters['finish_date__gt'] = finish_date__gt
                filters['pinned'] = False
            else:
                filters['finish_date__gt'] = finish_date__gt
        if finish_date__lt:
            if pinned is not None and not pinned:
                filters['finish_date__lt'] = finish_date__lt
                filters['pinned'] = False
            else:
                filters['finish_date__lt'] = finish_date__lt
        if status:

            filters['status__in'] = status
        if orders:
            self.obj = self.obj.order_by(*orders)
        if type_finish_date and int(type_finish_date) in [0, 1]:
            filters['type_finish_date'] = int(type_finish_date)
        if estimate_time == "null":
            filters['estimate_time__isnull']=True
        if estimate_time__gt:
            filters['estimate_time__gt'] = int(estimate_time__gt)
        if estimate_time__lt:
            filters['estimate_time__lt'] = int(estimate_time__lt)
        if assigned:
            if assigned == "me":
                filters['owner__pk'] = self.request.user.pk
            elif self.request.user.is_team_mate(assigned):
                filters['owner__pk'] = assigned
            elif assigned == "all":
                filters['owner__pk__in'] = self.request.user.all_team_mates_and_self()
            else:
                raise exceptions.PermissionDenied
        else:
            filters['owner__pk'] = self.request.user.pk
        if tags:
            if tags == ["null"]:
                self.obj = self.obj.filter(tags=None).distinct()
            else:
                for tag_id in tags:
                    if int(tag_id) not in self.tag_list_ids:
                        raise exceptions.PermissionDenied
                self.obj = self.obj.filter(tags__in=tags).distinct()
        filters['is_active'] = True
        self.obj = self.obj.filter(**filters)
        self.obj = self.obj.prefetch_related('steps', "task_list__share_with", "tags")
        db_time = time.time() - db_start
        return self.obj

    def get(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)
        return Response(self._filters_tags(serializer.data, self.tag_list_ids))

    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.pk
        if not 'owner' in data or not data['owner']:
            data['owner'] = data['author']

        form = TaskCreateForm(data)
        taskStepFormSet = modelformset_factory(TaskStep, form=TaskStepFormCreate)
        if form.is_valid():
            task = form.save()
            #adding steps TODO usunąć dublujący się kod dodający formsety, np przez mixin
            if "steps" in data and len(data['steps']) > 0:
                formset = taskStepFormSet(data['steps'], queryset=TaskStep.objects.filter(task=task).order_by("order"),
                                          prefix="steps")
                if formset.is_valid():
                    for one_form in formset:
                        step = one_form.save(commit=False)
                        step.task_id = task.id
                        step.author = request.user
                        step.owner = task.owner
                        step.save()
            Task.create_notification(old_task=None, new_task=task, request=request)
            data = TaskSerializer(task).data
            data["message"] = _("Task has been saved successfully.")
            result = Response(data, status=status.HTTP_201_CREATED)
        else:
            result = Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return result


class TaskDetail(generics.RetrieveUpdateDestroyAPIView, FiltersTagMixin):
    """
    Widok do edycji detali listy
    """
    model = Task
    queryset = Task.objects.filter(is_active=True)
    serializer_class = TaskSerializer
    renderer_classes = [JSONRenderer]
    
    def put(self, request, pk, format=None):

        old_task = self.get_object()
        data = request.data
        form = TaskEditForm(instance=self.get_object(), data=data, user=request.user)
        TaskStepFormSet = inlineformset_factory(Task, TaskStep, exclude=[])
        formset_blank = TaskStepFormSet(instance=old_task, prefix="steps")
        if form.is_valid():
            task = form.save()
             #adding steps
            if "steps" in data and len(data['steps']) > 0:
                formset = TaskStepFormSet(data['steps'], instance=task, prefix="steps")
                if formset.is_valid():

                    instance = formset.save()
                    steps_finished = 0
                    for step in instance:
                        step.task_id = task.id
                        step.author = request.user
                        step.owner = task.owner
                        if 'status' in form.changed_data and form.cleaned_data['status'] in [0, 1]:
                            step.status = task.status
                        step.save()
                        if step.status:
                            steps_finished += 1
                    if 'status' in form.changed_data and task.status == 0:
                        task.percent = 0
                    elif len(instance) > 0:
                        task.percent = int(float(steps_finished)/float(len(instance))*100)
                        if task.percent == 100:
                            task.status = 1
                        else:
                            task.status = 0
                    else:
                        task.percent = 0
                    task.save()
                else:
                    return Response(formset.errors, status=status.HTTP_400_BAD_REQUEST)
            Task.create_notification(old_task=old_task, new_task=task, request=request, form=form)
            data = TaskSerializer(task, context={"request": request}).data
            data["message"] = _("Task has been changed successfully.")
            return Response(self._filters_tags(data, Tag.objects.filter(author__pk=self.request.user.pk).values_list("id", flat=True)), status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        my_task = self.get_object()
        form = TaskDeleteForm(user=request.user, instance=my_task, data=self.kwargs)
        if form.is_valid():
            my_task.is_active = False
            my_task.save()
            return Response({'id': my_task.id, 'message': _('Task has been deleted successfully.')}, status=status.HTTP_200_OK)

        return Response(form.errors, status=status.HTTP_403_FORBIDDEN)

class TasksPostponeToToday(APIView):

    def _get_tasks_query(self):
        return Task.objects.filter(owner__pk=self.request.user.pk, status=0, finish_date__lt=datetime.today())

    def post(self, request, *args, **kwargs):
        self._get_tasks_query().update(finish_date=datetime.today())
        data = TaskSerializer(Task.objects.filter(owner__pk=self.request.user.pk, status=0, finish_date=datetime.today()), many=True).data
        return Response(data, status=status.HTTP_200_OK)






# def started(sender, **kwargs):
#     global started
#     global serializer_time
#     serializer_time = 0
#     started = time.time()
#
# def finished(sender, **kwargs):
#     total = time.time() - started
#     api_view_time = dispatch_time - (render_time + serializer_time + db_time)
#     request_response_time = total - dispatch_time
#
#     print ("Database lookup               | %.4fs" % db_time)
#     print ("Serialization                 | %.4fs" % serializer_time)
#     print ("Django request/response       | %.4fs" % request_response_time)
#     print ("API view                      | %.4fs" % api_view_time)
#     print ("Response rendering            | %.4fs" % render_time)
#
# request_started.connect(started)
# request_finished.connect(finished)