# encoding: utf-8
import datetime
import hashlib
import posixpath
import time

from cool.model import BaseModel
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


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
