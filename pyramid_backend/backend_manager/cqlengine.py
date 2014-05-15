from __future__ import absolute_import
__author__ = 'tarzan'

import inspect
from collections import OrderedDict
from pyramid.decorator import reify
import importlib
from . import Manager, _name_to_words, AttrDisplayConf as _BaseAttrDisplayConf
from cqlengine.models import (
    Model as CQLEngineModel,
)
from cqlengine.exceptions import  ValidationError
from cqlengine.query import ModelQuerySet


def factory(config):
    """
    :type config: pyramid.config.Configurator
    """
    def _create_manager(model):
        if inspect.isclass(model) and issubclass(model, CQLEngineModel):
            return CQLEngineManager(model)
        return None

    return _create_manager


class AttrDisplayConf(_BaseAttrDisplayConf):
    def values(self, obj):
        vals = self.value(obj)
        if isinstance(vals, ModelQuerySet):
            vals = list(vals)
        if isinstance(vals, (list, tuple)):
            return vals[:self.limit]
        return [vals, ]


class CQLEngineManager(Manager):

    __attr_display_conf_class__ = AttrDisplayConf

    @reify
    def queryset(self):
        """
        Get query set for current model
        :rtype cqlengine.query.ModelQuerySet
        """
        return self.Model.objects

    @reify
    def column_names(self):
        return [c_name for c_name in self.Model._columns]

    def column(self, col_name):
        return getattr(self.Model, col_name)

    @property
    def __default_list__columns_to_display__(self):
        columns = OrderedDict(zip(self.column_names, [_name_to_words(n) for n in self.column_names]))
        columns[self.id_attr] = '#'
        return columns

    @property
    def __default_detail__columns_to_display__(self):
        columns = OrderedDict(zip(self.column_names, [_name_to_words(n) for n in self.column_names]))
        columns[self.id_attr] = '#'
        return columns

    @property
    def __default_detail__relations_to_display__(self):
        return []

    def create(self, data):
        obj = self.Model.create(**data)
        return obj

    def update(self, obj, data):
        obj.update(**data)
        return obj

    def delete(self, obj):
        obj.delete()

    def fetch_objects(self, filters, page=1):
        criteria = []
        for name, value in filters.items():
            if name in self.column_names:
                criteria.append(self.column(name) == value)
        limit = self.list__items_per_page
        offset = (page-1)*limit
        objs = self.queryset.filter(*criteria).limit(offset + limit)
        return list(objs)[-limit:]

    def count_objects(self, filters):
        return 10000
        criteria = []
        for name, value in filters.items():
            if name in self.column_names:
                criteria.append(self.column(name) == value)
        return self.queryset.filter(*criteria).count()
