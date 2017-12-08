#-*- coding: utf-8 -*-

from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from dashboard.lists.models import List
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    daily_summary_hour = serializers.TimeField(format='iso-8601', input_formats=None)

    class Meta:
        model = User
        fields = ('username', 'avatar', 'id', "email", "facebook_connection", "google_connection",
                  "avatar_url", "inbox_pk", "daily_summary_hour", "date_joined", "removes_me_from_shared_list",
                  "shares_list_with_me", "assigns_task_to_me", "completes_task_from_shared_list",
                  "changes_task_from_shared_list_that_is_assigned_to_me",
                  "changes_task_from_shared_list_that_i_assigned_to_him_her", "leaves_shared_list",
                  "order_tasks_dashboard", "deletes_list_shared_with_me", "default_task_view_today_view",
                  "default_task_view_overdue_view", "default_task_view_future_view", "default_task_view_tags_view",
                  "default_task_view")


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'avatar', 'id', "email", "avatar_url")

#Import loop.
class SimpleListSerializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = ("id", "name", "color")


class SimpleUserWithListsSerializer(serializers.ModelSerializer):

    share_with = SimpleListSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'avatar', 'id', 'email', 'avatar_url', "share_with")

    def to_representation(self, instance):
        ret = super(SimpleUserWithListsSerializer, self).to_representation(instance)
        user_lists_pk = self._context['user_lists_pk'] if 'user_lists_pk' in self._context else []
        for i, arg in enumerate(ret['share_with']):
            if arg['id'] not in user_lists_pk:
                del ret['share_with'][i]
        return ret
