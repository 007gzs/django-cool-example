# encoding: utf-8

from cool.views import ViewSite, CoolBFFAPIView, ErrorCode, CoolAPIException
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import fields

from . import serializer, models

site = ViewSite(name='demo', app_name='demo')


@site
class UserLogin(CoolBFFAPIView):

    name = _('user login')
    response_info_serializer_class = serializer.UserSerializer

    def get_context(self, request, *args, **kwargs):
        user = authenticate(self, base_username=request.params.username, base_password=request.params.password)
        if user is None:
            raise CoolAPIException(ErrorCode.ERR_DEMO_NOTFOUND)
        login(request, user)
        return serializer.UserSerializer(user).data

    class Meta:
        param_fields = (
            ('username', fields.CharField(label=_('login name'))),
            ('password', fields.CharField(label=_('password'))),
        )


@site
class UserRegister(CoolBFFAPIView):

    name = _('user register')
    response_info_serializer_class = serializer.UserSerializer

    def get_context(self, request, *args, **kwargs):
        user = models.User.objects.get_all_queryset().filter(
            Q(username=request.params.username) | Q(mobile=request.params.mobile)).first()
        if user is not None:
            if user.username == request.params.username:
                raise CoolAPIException(ErrorCode.ERR_DEMO_DUPLICATE_USERNAME)
            elif user.mobile == request.params.mobile:
                raise CoolAPIException(ErrorCode.ERR_DEMO_DUPLICATE_MOBILE)
        user = models.User()
        user.username = request.params.username
        user.mobile = request.params.mobile
        user.nickname = request.params.nickname
        user.name = request.params.name
        user.avatar = request.params.avatar
        user.set_password(request.params.password)
        try:
            user.save(force_insert=True)
        except IntegrityError as exc:
            if exc.args[0] == 1062:
                if exc.args[1].find('username') >= 0:
                    exc = CoolAPIException(ErrorCode.ERR_DEMO_DUPLICATE_USERNAME)
                elif exc.args[1].find('mobile') >= 0:
                    exc = CoolAPIException(ErrorCode.ERR_DEMO_DUPLICATE_MOBILE)
            raise exc
        user = authenticate(self, base_username=request.params.username, base_password=request.params.password)
        if user is None:
            raise CoolAPIException(ErrorCode.ERR_DEMO_NOTFOUND)
        login(request, user)
        return serializer.UserSerializer(user).data

    class Meta:
        param_fields = (
            ('username', fields.CharField(label=_('login name'), max_length=64,
                                          help_text=_('Help text for field. It will show in api document'))),
            ('password', fields.CharField(label=_('password'))),
            ('mobile', fields.RegexField(r'1\d{10}', label=_('mobile number'))),
            ('nickname', fields.CharField(label=_('nick name'), max_length=255)),
            ('name', fields.CharField(label=_('name'), default='', max_length=255)),
            ('avatar', fields.ImageField(label=_('avatar'), default=None)),
        )


class UserApi(CoolBFFAPIView):

    need_permissions = ()

    def get_context(self, request, *args, **kwargs):
        raise NotImplementedError

    def check_api_permissions(self, request, *args, **kwargs):
        if not isinstance(request.user, models.User):
            raise CoolAPIException(ErrorCode.ERR_DEMO_NOLOGIN)
        for permission in self.need_permissions:
            if not request.user.has_perm(permission):
                raise CoolAPIException(ErrorCode.ERR_DEMO_PERMISSION)

    class Meta:
        path = '/'


@site
class UserLogout(UserApi):

    name = _('user logout')

    def get_context(self, request, *args, **kwargs):
        logout(request)
        return None


@site
class UserInfo(UserApi):

    name = _('user info')
    response_info_serializer_class = serializer.UserSerializer

    def get_context(self, request, *args, **kwargs):
        return serializer.UserSerializer(request.user).data


@site
class UserEdit(UserApi):

    name = _('change user info')
    response_info_serializer_class = serializer.UserSerializer

    def get_context(self, request, *args, **kwargs):
        user = request.user
        if request.params.mobile is not None:
            user.mobile = request.params.mobile
        if request.params.nickname is not None:
            user.nickname = request.params.nickname
        if request.params.name is not None:
            user.name = request.params.name
        if request.params.avatar is not None:
            user.avatar = request.params.avatar
        if request.params.password is not None:
            user.set_password(request.params.password)
        user.save_changed()
        return serializer.UserSerializer(user).data

    class Meta:
        param_fields = (
            ('password', fields.CharField(label=_('password'), default=None)),
            ('mobile', fields.RegexField(r'1\d{10}', label=_('mobile number'), default=None)),
            ('nickname', fields.CharField(label=_('nick name'), default=None, max_length=255)),
            ('name', fields.CharField(label=_('name'), default=None, max_length=255)),
            ('avatar', fields.ImageField(label=_('avatar'), default=None)),
        )


@site
class PermissionTest(UserApi):
    name = _('user permission test')

    need_permissions = ('test.test', )

    def get_context(self, request, *args, **kwargs):
        return 'ok'


@site
class PermissionTest2(UserApi):
    name = _('user permission test2')

    need_permissions = ('test.test2', )

    def get_context(self, request, *args, **kwargs):
        return 'ok'


urls = site.urls
urlpatterns = site.urlpatterns
