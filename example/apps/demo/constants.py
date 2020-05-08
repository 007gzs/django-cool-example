# encoding: utf-8

from django.utils.translation import gettext_lazy as _
from cool.core import Constants


class Gender(Constants):
    MALE = (1, _('Male'))
    FEMALE = (2, _('Female'))
