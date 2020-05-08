# encoding: utf-8

from django.db.models import Q

from . import models


class BaseUserBackend:

    def authenticate(self, request, base_username=None, base_password=None, base_mobile=None, **kwargs):
        if base_username is not None and base_password is not None:
            user = models.User.objects.filter(username=base_username).first()
            if user and user.check_password(base_password) and self.user_can_authenticate(user):
                return user
        elif base_mobile is not None:
            user = models.User.objects.filter(username=base_username).first()
            if user and self.user_can_authenticate(user):
                return user
        return None

    @classmethod
    def user_can_authenticate(cls, user):
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    @classmethod
    def _get_all_permissions(cls, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        permissions = models.Permission.objects.all()
        if not user_obj.is_superuser:
            user_modules_field_related = models.User._meta.get_field('modules').related_query_name()
            user_permissions_field_related = models.User._meta.get_field('permissions').related_query_name()
            user_groups_field_related = models.User._meta.get_field('groups').related_query_name()
            group_modules_field_related = models.Group._meta.get_field('modules').related_query_name()
            group_permissions_field_related = models.Group._meta.get_field('permissions').related_query_name()
            permission_module_field_name = models.Permission._meta.get_field('module').name
            filters = (
                (group_permissions_field_related, user_groups_field_related),
                (user_permissions_field_related, ),
                (permission_module_field_name, user_modules_field_related),
                (permission_module_field_name, group_modules_field_related, user_groups_field_related),
            )
            q = Q()
            for f in filters:
                q |= Q(**{'__'.join(f): user_obj})
            permissions = permissions.filter(q)
        perms = permissions.values_list('module_id', 'code').order_by()
        return set("%s.%s" % (ct, name) for ct, name in perms)

    @classmethod
    def get_all_permissions(cls, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = cls._get_all_permissions(user_obj)
        return user_obj._perm_cache

    @classmethod
    def has_perm(cls, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm in cls.get_all_permissions(user_obj, obj)

    def get_user(self, user_id):
        user = models.User.get_obj_by_pk_from_cache(user_id)
        return user if self.user_can_authenticate(user) else None
