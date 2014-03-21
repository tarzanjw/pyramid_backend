__author__ = 'tarzan'
import re
import inspect
import importlib
from pyramid.decorator import reify

_managers_factory = []

def _name_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def _name_to_words(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    words = re.split('[_\s]+', name)
    def capitalize(s):
        return s[0].upper() + s[1:]
    return ' '.join([capitalize(w) for w in words])

def create_backend_manager(model):
    """
    create backend manager for a model
    :rtype Manager
    """
    for mf in _managers_factory:
        mgr = mf(model)
        if mgr:
            return mgr

    raise NotImplementedError('Can not find backend manager for model "%s"' % model.__name__)

def register_manager_factory(factory):
    global _managers_factory
    _managers_factory.append(factory)

def get_manager(model):
    """
    get backend manager for a model
    :rtype Manager
    """
    try:
        return model.__backend_manager__
    except AttributeError:
        manager = create_backend_manager(model)
        model.__backend_manager__ = manager
        return manager

class Manager(object):
    def __init__(self, model):
        """
        :type model: class
        """
        assert inspect.isclass(model)
        self.Model = model
        self.actions = {}

    @reify
    def default_actions(self):
        return {
        'list': {
            'route_name': 'admin_site',
            'context': self.ModelResource,
            'attr': 'action_list',
            'renderer': 'pyramid_backend:templates/list.mak',
            'permission': 'list',
            '_icon': 'list',
            '_label': self.display_name + u' list',
        },
        'create': {
            'route_name': 'admin_site',
            'context': self.ModelResource,
            'name': 'create',
            'attr': 'action_create',
            'renderer': 'pyramid_backend:templates/create.mak',
            'permission': 'create',
            '_icon': 'plus',
            '_label': u'Create new ' + self.display_name,
        },
        'detail': {
            'route_name': 'admin_site',
            'context': self.ObjectResource,
            'attr': 'action_detail',
            'renderer': 'pyramid_backend:templates/detail.mak',
            'permission': 'detail',
            '_icon': 'eye-open',
            '_label': u'View %s detail',
        },
        'update': {
            'route_name': 'admin_site',
            'context': self.ObjectResource,
            'name': 'update',
            'attr': 'action_update',
            'renderer': 'pyramid_backend:templates/update.mak',
            'permission': 'update',
            '_icon': 'pencil',
            '_label': u'Update %s',
        },
        'delete': {
            'route_name': 'admin_site',
            'context': self.ObjectResource,
            'name': 'delete',
            'attr': 'action_delete',
            'renderer': 'pyramid_backend:templates/update.mak',
            'permission': 'delete',
            '_icon': 'remove',
            '_label': u'Delete %s',
            '_onclick': u"alert('%s');"
        },
    }

    _configurable_properties = [
        'slug',
        'display_name',
        'schema_cls',
        'id_attr',
        'list__column_names_to_display',
        'detail__column_names_to_display',
        'list__items_per_page',
    ]

    def __getattribute__(self, name):
        if name in Manager._configurable_properties:
            try:
                val = getattr(self.Model, '__backend_' + name + '__')
            except AttributeError:
                val = getattr(self, '__default_' + name + '__')
            setattr(self, name, val)
            return val
        return super(Manager, self).__getattribute__(name)

    __default_schema_cls__ = None
    __default_id_attr__ = 'id'
    __default_list__items_per_page__ = 50

    @property
    def __default_slug__(self):
        return _name_to_underscore(self.Model.__name__)


    @property
    def __default_display_name__(self):
        return _name_to_words(self.Model.__name__)

    @property
    def __default_list__column_names_to_display__(self):
        columns = dict(zip(dir(self.Model), dir(self.Model)))
        columns[self.id_attr] = '#'
        return columns

    @property
    def __default_detail__column_names_to_display__(self):
        columns = dict(zip(dir(self.Model), dir(self.Model)))
        columns[self.id_attr] = '#'
        return columns

    @reify
    def ModelResource(self):
        from pyramid_backend import resources
        return resources.model_resource_class(self.Model)

    @reify
    def ObjectResource(self):
        from pyramid_backend import resources
        return resources.object_resource_class(self.Model)

    def configure_actions(self, actions):
        if actions is None:
            actions = self.default_actions
        elif isinstance(actions, (list, tuple,)):
            actions = {k:v for k,v in self.default_actions.items() if k in actions}
        elif isinstance(actions, dict):
            actions = {k:(v if k not in actions else v if v else actions[k]) for k,v in actions}
        self.actions = actions

    def object_id(self, obj):
        return getattr(obj, self.id_attr)

    def create(self, data):
        raise NotImplementedError()

    def update(self, obj, data):
        raise NotImplementedError()

    def fetch_objects(self, filters, page=1):
        raise NotImplementedError()

    def count_objects(self, filters):
        raise NotImplementedError()

    def find_object(self, id_value):
        raise NotImplementedError()


from .sqlalchemy import SQLAlchemyManager