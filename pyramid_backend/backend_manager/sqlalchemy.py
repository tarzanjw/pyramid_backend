from __future__ import absolute_import
__author__ = 'tarzan'

from collections import OrderedDict
from pyramid.decorator import reify
from paste.deploy.util import lookup_object
from . import Manager, _name_to_words
import logging

logger = logging.getLogger(__name__)

def factory(config):
    return lambda m: None

try:
    from sqlalchemy import func, Table
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.orm.properties import ColumnProperty
    from sqlalchemy.orm import class_mapper
    from sqlalchemy.orm.exc import UnmappedClassError
    _sqlalchemy_is_available = True
except ImportError:  # sqlalchemy is not available
    _sqlalchemy_is_available = False
    func = object()
    class Table(object):
        pass
    class InstrumentedAttribute(object):
        pass
    class ColumnProperty(object):
        pass
    class UnmappedClassError(object):
        pass

if _sqlalchemy_is_available:
    DBSession = None
    """:type : sqlalchemy.orm.session.Session"""

    def factory(config):
        """
        :type config: pyramid.config.Configurator
        """
        global DBSession
        settings = config.get_settings()
        dbsession_path = settings.get('pyramid_backend.sqlalchemy.dbsession')
        if not dbsession_path:
            logger.warn('You have not configured dbsession for pyramid_backend '
                        'sqlalchemy adapter at '
                        '"pyramid_backend.sqlalchemy.dbsession"')
            return lambda m: None

        DBSession = lookup_object(dbsession_path)

        def _create_manager(model):
            # verify model is an ORM class of SQLAlchemy or not
            # if not, just return None
            try:
                mapper = class_mapper(model)
            except UnmappedClassError:
                return None
            return SQLAlchemyManager(model)

        return _create_manager


    class SQLAlchemyManager(Manager):

        @reify
        def column_names(self):
            def is_column(col):
                return \
                    isinstance(col, InstrumentedAttribute) \
                    and isinstance(col.property, ColumnProperty)
            col_names_in_order = class_mapper(self.Model).local_table.columns.keys()
            c2a = {c.name: a for a, c in self.Model.__dict__.items() if is_column(c)}
            col_names = [c2a[col] for col in col_names_in_order]
            return list(self.id_attr) + [c for c in col_names if c not in self.id_attr]

        def column(self, col_name):
            return getattr(self.Model, col_name)

        @property
        def _foreignkey_names(self):
            return [rel.key for rel in class_mapper(self.Model).relationships]

        @property
        def __default_detail__relations_to_display__(self):
            return OrderedDict(zip(
                self._foreignkey_names,
                [_name_to_words(n) for n in self._foreignkey_names]
            ))

        def create(self, data):
            obj = self.Model()
            for k, v in data.items():
                setattr(obj, k, v)
            DBSession.add(obj)
            DBSession.flush()
            return obj

        def update(self, obj, data):
            for k, v in data.items():
                setattr(obj, k, v)
            DBSession.merge(obj)
            DBSession.flush()
            return obj

        def delete(self, obj):
            DBSession.delete(obj)
            DBSession.flush()

        def fetch_objects(self, filters, fulltext=True, page=1):
            query = DBSession.query(self.Model)
            for name, value in filters.items():
                if name in self.column_names:
                    if fulltext:
                        query = query.filter(self.column(name)
                                             .like("%%%s%%" % value))
                    else:
                        query = query.filter(self.column(name) == value)
            limit = self.list__items_per_page
            offset = (page-1)*limit
            id_cols = [self.column(id_attr) for id_attr in self.id_attr]
            for id_col in id_cols:
                query = query.order_by(id_col.desc())
            query = query.offset(offset).limit(limit)
            return query

        def count_objects(self, filters):
            cols = [getattr(self.Model, pk_col) for pk_col in self.id_attr]
            query = DBSession.query(func.count(*cols))

            for name, value in filters.items():
                if name in self.column_names:
                    query = query.filter(self.column(name).like("%%%s%%" % value))

            return query.scalar()