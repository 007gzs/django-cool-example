# encoding: utf-8

from cool.core import Constants
from django.utils.translation import gettext_lazy as _


class Gender(Constants):
    MALE = (1, _('Male'))
    FEMALE = (2, _('Female'))
