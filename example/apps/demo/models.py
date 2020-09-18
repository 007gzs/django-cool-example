# encoding: utf-8
from cool.admin import admin_register
from django.contrib.auth.base_user import AbstractBaseUser
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _
from cool import model

from example.core import utils
from . import constants


class Module(utils.ExampleBaseModel):
    name = models.CharField(_('module name'), max_length=255)
    code = models.CharField(_('module code'), max_length=100, unique=True)

    class Meta:
        verbose_name = verbose_name_plural = _('module')


@admin_register(
    list_display=['module', 'name'],
    list_filter=['module', ],
    change_view_readonly_fields=['code', ],
    list_editable=['name', 'module']
)
class Permission(utils.ExampleBaseModel):
    name = models.CharField(_('permission name'), max_length=255)
    code = models.CharField(_('permission code'), max_length=100)
    module = model.ForeignKey(
        Module, verbose_name=_('module'), to_field='code', db_column='module_code', on_delete=models.PROTECT
    )

    def get_code(self):
        return '%s.%s' % (self.module_id, self.code)

    def __str__(self):
        return self.module.name + '-' + self.name

    class Meta:
        unique_together = ('module', 'code')
        verbose_name = verbose_name_plural = _('permission')


@admin_register
class Group(utils.ExampleBaseModel):
    name = models.CharField(_('group name'), max_length=255)
    modules = models.ManyToManyField(Module, verbose_name=_('group modules'), blank=True)
    permissions = models.ManyToManyField(Permission, verbose_name=_('group permissions'), blank=True)

    class Meta:
        verbose_name = verbose_name_plural = _('system group')


class User(model.AbstractUserMixin, utils.ExampleBaseModel, AbstractBaseUser):
    USERNAME_FIELD = 'username'
    username = models.CharField(_('login name'), max_length=64, unique=True)
    mobile = models.CharField(
        _('mobile number'), max_length=12, unique=True, validators=[validators.RegexValidator(r'1\d{10}')]
    )
    nickname = models.CharField(_('nick name'), max_length=255, blank=True, default='')
    name = models.CharField(_('name'), max_length=255, blank=True, default='')
    gender = models.IntegerField(_('gender'), choices=constants.Gender.get_choices_list())
    avatar = models.ImageField(
        _('avatar'), max_length=512, blank=True, default='', upload_to=utils.FileUploadTo('avatar/%Y/%m%d/')
    )
    is_superuser = models.BooleanField(_('is superuser'), default=False)
    modules = models.ManyToManyField(Module, verbose_name=_('user modules'), blank=True)
    permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True)
    groups = models.ManyToManyField(Group, verbose_name=_('user groups'), blank=True)

    @classmethod
    def get_search_fields(cls):
        ret = super().get_search_fields()
        ret.add('nickname')
        ret.add('modules__name')
        return ret

    def __str__(self):
        return self.nickname

    def get_all_permissions(self, obj=None):
        from .backend import BaseUserBackend
        return BaseUserBackend.get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        from .backend import BaseUserBackend

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return BaseUserBackend.has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)

    class Meta:
        verbose_name = verbose_name_plural = _('system user')
