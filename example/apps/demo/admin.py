# encoding: utf-8

from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from example.core import utils
from . import models


class BaseUserAdmin(utils.ExampleBaseModelAdmin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nickname', 'name', 'mobile', 'avatar')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser', 'groups', 'permissions', 'modules')}),
    )

    exclude_list_display = ('password', )
    filter_horizontal = ('groups', 'permissions', 'modules')


utils.site_register(models.User, BaseUserAdmin, list_filter=('groups', 'gender'))
utils.site_register(models.Module, list_display=[], change_view_readonly_fields=['code', ])
utils.site_register(
    models.Permission,
    list_display=['module', ],
    list_filter=['module', ],
    change_view_readonly_fields=['code', ]
)
utils.site_register(models.Group)
