# encoding: utf-8

from cool.views import CoolAPIException, CoolBFFAPIView, ErrorCode, ViewSite, utils
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework import fields

from . import constants, models, serializer

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
        return serializer.UserSerializer(user, request=request).data

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
        user = models.User.objects.filter(
            Q(username=request.params.username) | Q(mobile=request.params.mobile)
        ).first()
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
        user.gender = request.params.gender
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
        return serializer.UserSerializer(user, request=request).data

    class Meta:
        param_fields = (
            ('username', fields.CharField(label=_('login name'), max_length=64,
                                          help_text=_('Help text for field. It will show in api document'))),
            ('password', fields.CharField(label=_('password'))),
            ('gender', fields.ChoiceField(label=_('gender'), choices=constants.Gender.get_choices_list())),
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
        return serializer.UserSerializer(request.user, request=request).data


class EditMixin:

    model = None
    edit_fields = []

    @classmethod
    def get_extend_param_fields(cls):
        ret = list()
        ret.extend(super().get_extend_param_fields())
        if cls.model is not None:
            for edit_field in cls.edit_fields:
                ret.append((edit_field, utils.get_rest_field_from_model_field(cls.model, edit_field, default=None)))
        return tuple(ret)

    def get_obj(self, request):
        raise NotImplementedError

    def modify_obj(self, request, obj):
        for edit_field in self.edit_fields:
            value = getattr(request.params, edit_field, None)
            if value is not None:
                setattr(obj, edit_field, value)

    def save_obj(self, request, obj):
        obj.full_clean()
        obj.save_changed()

    def serializer_response(self, data, request):
        return self.response_info_serializer_class(data, request=request).data

    def get_context(self, request, *args, **kwargs):
        with transaction.atomic():
            obj = self.get_obj(request)
            self.modify_obj(request, obj)
            self.save_obj(request, obj)
        return self.serializer_response(obj, request=request)


@site
class UserEdit(EditMixin, UserApi):

    name = _('change user info')
    response_info_serializer_class = serializer.UserSerializer
    model = models.User
    edit_fields = ['gender', 'mobile', 'nickname', 'name', 'avatar']

    def get_obj(self, request):
        return request.user

    def modify_obj(self, request, obj):
        super().modify_obj(request, obj)
        if request.params.password is not None:
            obj.set_password(request.params.password)

    class Meta:
        param_fields = (
            ('password', fields.CharField(label=_('password'), default=None)),
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


@site
class Test(CoolBFFAPIView):
    def get_context(self, request, *args, **kwargs):
        return render(request, request.params.template)

    class Meta:
        param_fields = (
            ('template', fields.CharField()),
        )


@site
class TestRe(CoolBFFAPIView):
    def get_context(self, request, *args, **kwargs):
        return request.params.test

    class Meta:
        param_fields = (
            ('app_id', fields.CharField()),
            ('test', fields.JSONField()),
        )
        path = "(?P<app_id>[0-9a-zA-Z]+)/testre"


urls = site.urls
urlpatterns = site.urlpatterns
