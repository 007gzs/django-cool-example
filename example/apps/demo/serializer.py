# encoding: utf-8

from rest_framework import serializers

from cool import views

from . import models
from .backend import BaseUserBackend


class UserSerializer(views.BaseSerializer):
    permissions = serializers.SerializerMethodField("all_permissions", label='权限列表')

    def all_permissions(self, obj):
        return BaseUserBackend().get_all_permissions(obj)

    class Meta:
        model = models.User
        fields = ('id', 'username', 'nickname', 'mobile', 'name', 'avatar', 'permissions', 'is_superuser')
