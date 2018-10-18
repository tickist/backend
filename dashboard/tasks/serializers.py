#-*- coding: utf-8 -*-
from rest_framework import serializers
from dashboard.lists.serializers import ListSerializer, SimpleListSerializer
from dashboard.tasks.models import Task, TaskStep, Tag
from users.serializers import SimpleUserSerializer


class TagSerializer(serializers.ModelSerializer):


    class Meta:
        model = Tag
        fields = ("id", "name", "author", "creation_date", "modification_date", "tasks_counter")


class SimpleTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ("id", "name", "author", "creation_date", "modification_date", "tasks_counter")


class TaskStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskStep
        fields = ("id", "name", "task", "author", "owner", "creation_date", "modification_date", "status", "order")


class TaskSerializer(serializers.ModelSerializer):
    task_project = SimpleListSerializer(source='task_list')
    finish_date = serializers.DateField(format='%d-%m-%Y')
    finish_time = serializers.TimeField(format="%H:%M")
    steps = TaskStepSerializer(many=True)
    tags = SimpleTagSerializer(many=True)
    owner = SimpleUserSerializer()
    author = SimpleUserSerializer()


    class Meta:
        model = Task
        fields = ("id", "name", 'owner', 'author', 'priority', 'description', 'task_list', 'task_project', 'task_list_pk',
                  'estimate_time', 'time', 'ancestor', 'creation_date', 'modification_date', 'finish_date',
                  'finish_time', 'type_finish_date', 'percent', 'repeat', 'repeat_delta', 'from_repeating', 'status',
                  'when_complete', 'owner_pk', 'is_active', 'suspend_date', 'tags', 'pinned',
                  'finish_date_dateformat', 'steps'
        )





