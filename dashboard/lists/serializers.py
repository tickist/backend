#-*- coding: utf-8 -*-

from django.conf import settings
from users.serializers import UserSerializer, SimpleUserSerializer
from rest_framework import serializers
from dashboard.lists.models import List, ShareListPending



class ListSerializer(serializers.ModelSerializer):
    #lists = serializers.Field(source='get_serialized_descendants')
    lists = serializers.SerializerMethodField('get_descendant')
    tags = serializers.SerializerMethodField()
    share_with = SimpleUserSerializer(many=True)

    class Meta:
        model = List
        fields = ("id", "name", "description", "logo", "owner", "is_inbox", "share_with", "ancestor", "creation_date",
                  "modification_date", "color", "is_active", "default_priority", "default_finish_date",
                  "default_type_finish_date", "tasks_counter", "task_finish_date", "lists", "share_with", "tags",
                  "level", "get_all_descendants", "task_view", "dialog_time_when_task_finished")

    def get_descendant(self, obj):
        request = self.context['request'] if 'request' in self.context else None
        user = getattr(request, 'user', None)
        return obj.get_serialized_descendants(user, request)

    def get_tags(self, obj):
        request = self.context['request'] if 'request' in self.context else None
        user = getattr(request, 'user', None)
        return obj.get_tags(user)

    def to_representation(self, instance):
        ret = super(ListSerializer, self).to_representation(instance)
        ret['share_with'] = ret['share_with'] + ShareListPendingSerializer(ShareListPending.objects.
                                                            filter(is_active=True, list=instance), many=True).data
        return ret


class SimpleListSerializer(serializers.ModelSerializer):

    share_with = SimpleUserSerializer(many=True)

    class Meta:
        model = List
        fields = ("id", "name", "color", "share_with", "dialog_time_when_task_finished")


class ShareListPendingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShareListPending
        fields = ("is_active", "email")

    def to_representation(self, instance):
        ret = super(ShareListPendingSerializer, self).to_representation(instance)
        ret['username'] = instance.email
        ret['avatar_url'] = "/" + settings.DEFAULT_AVATAR
        return ret