# encoding: utf-8

from cool import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class BaseUserAdmin(admin.BaseModelAdmin, UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nickname', 'name', 'gender', 'mobile', 'avatar')}),
        (_('Permissions'), {'fields': ('is_superuser', 'groups', 'permissions', 'modules')}),
    )
    search_fields = ()
    exclude_list_display = ('password', )
    filter_horizontal = ('groups', 'permissions', 'modules')
    change_view_readonly_fields = ['username', ]


admin.site_register(models.User, BaseUserAdmin, list_filter=('groups', 'gender', 'modules'), addable=False)
admin.site_register(models.Module, change_view_readonly_fields=['code'], list_display=['name'], list_editable=['name'])
