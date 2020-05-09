# encoding: utf-8
import datetime
import hashlib
import posixpath
import time

from cool.views import get_api_doc
from django.db import models
from django.http import HttpResponse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from cool.model import BaseModel
from cool.admin import BaseModelAdmin, DateRangeFieldFilter, site_register as cool_site_register


class ExampleBaseModelAdmin(BaseModelAdmin):
    list_filter = ('create_time', 'modify_time')


def site_register(model_or_iterable, admin_class=None, site=None, add_base_list_filter=True, **options):
    if admin_class is None:
        admin_class = ExampleBaseModelAdmin
    if add_base_list_filter and 'list_filter' in options and admin_class.list_filter:
        new_list_filter = list(admin_class.list_filter)
        for field in options['list_filter']:
            if field not in new_list_filter:
                new_list_filter.append(field)
        options['list_filter'] = new_list_filter
    cool_site_register(model_or_iterable, admin_class, site, **options)


class ExampleBaseModel(BaseModel):
    id = models.BigAutoField(_('ID'), primary_key=True, editable=False)
    create_time = models.DateTimeField(_('Create Time'), auto_now_add=True, db_index=True, editable=False)
    modify_time = models.DateTimeField(_('Modify Time'), auto_now=True, db_index=True, editable=False)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return super().__str__()

    @classmethod
    def get_search_fields(cls):
        ret = super().get_search_fields()
        for field in cls._meta.fields:
            if field.name == 'name' and isinstance(field, models.CharField):
                ret.add(field.name)
        return ret

    class Meta:
        abstract = True


@deconstructible
class FileUploadTo(object):

    def __init__(self, base_path):
        self.base_path = base_path

    def __call__(self, instance, filename):
        dirname = datetime.datetime.now().strftime(self.base_path)
        extension = posixpath.splitext(filename)[1]
        data = "%s_%s" % (filename, time.time())
        file_hash = hashlib.sha1(data.encode('utf-8')).hexdigest()
        filename = "%s%s" % (file_hash, extension)
        return posixpath.join(dirname, filename)


def api_doc(request):
    return HttpResponse(get_api_doc(request), content_type='text/markdown;charset=utf-8')
