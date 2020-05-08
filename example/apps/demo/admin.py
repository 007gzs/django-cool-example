# encoding: utf-8

from cool.admin import site_register
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from example.core import utils
from . import models


class BaseUserAdmin(utils.ExampleBaseModelAdmin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nickname', 'name', 'mobile', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    exclude_list_display = ('password', )
    filter_horizontal = ('groups', 'user_permissions',)


site_register(models.User, BaseUserAdmin, list_filter=('groups',))
site_register(models.Module, utils.ExampleBaseModelAdmin, list_display=[], change_view_readonly_fields=['code', ])
site_register(
    models.Permission, utils.ExampleBaseModelAdmin, list_display=['module'], change_view_readonly_fields=['code', ]
)
site_register(models.Group, utils.ExampleBaseModelAdmin)
